from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from apps.products.models import Category, UnitOfMeasure, Product
from apps.vendors.models import Vendor, VendorContact, VendorProduct
from apps.inventory.models import Warehouse, Location, StockQuant
from apps.sales.models import (
    Customer, SalesQuotation, SalesQuotationLine,
    SalesOrder, SalesOrderLine, SalesInvoice, SalesInvoiceLine
)
from apps.purchasing.models import RequestForQuotation, RFQLine, PurchaseOrder, POLine
from apps.manufacturing.models import BillOfMaterials, BOMLine, ManufacturingOrder


class Command(BaseCommand):
    help = 'Seed database with dummy data for cafe ERP'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding database with dummy data...\n')
        
        self.create_uom()
        self.create_categories()
        self.create_products()
        self.create_vendors()
        self.create_warehouses()
        self.create_stock()
        self.create_customers()
        self.create_bom()
        self.create_rfq_and_po()
        self.create_quotations_and_orders()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))

    def create_uom(self):
        self.stdout.write('  Creating Units of Measure...')
        
        uoms_data = [
            {'name': 'Piece', 'symbol': 'pcs', 'category': 'unit', 'is_base_unit': True},
            {'name': 'Kilogram', 'symbol': 'kg', 'category': 'weight', 'is_base_unit': True},
            {'name': 'Gram', 'symbol': 'g', 'category': 'weight', 'ratio': Decimal('0.001')},
            {'name': 'Liter', 'symbol': 'L', 'category': 'volume', 'is_base_unit': True},
            {'name': 'Milliliter', 'symbol': 'ml', 'category': 'volume', 'ratio': Decimal('0.001')},
            {'name': 'Cup', 'symbol': 'cup', 'category': 'unit'},
            {'name': 'Pack', 'symbol': 'pack', 'category': 'unit'},
            {'name': 'Box', 'symbol': 'box', 'category': 'unit'},
        ]
        
        self.uoms = {}
        for data in uoms_data:
            uom, created = UnitOfMeasure.objects.get_or_create(
                symbol=data['symbol'],
                defaults=data
            )
            self.uoms[data['symbol']] = uom
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {len(uoms_data)} UoMs'))

    def create_categories(self):
        self.stdout.write('  Creating Categories...')
        
        categories_data = [
            {'name': 'Beverages', 'description': 'Coffee, tea, and other drinks'},
            {'name': 'Food', 'description': 'Pastries, cakes, and snacks'},
            {'name': 'Raw Materials', 'description': 'Ingredients for production'},
            {'name': 'Packaging', 'description': 'Cups, lids, bags, etc.'},
        ]
        
        self.categories = {}
        for data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            self.categories[data['name']] = cat
        
        # Sub-categories
        sub_categories = [
            {'name': 'Coffee', 'parent': 'Beverages'},
            {'name': 'Non-Coffee', 'parent': 'Beverages'},
            {'name': 'Pastry', 'parent': 'Food'},
            {'name': 'Cake', 'parent': 'Food'},
        ]
        
        for data in sub_categories:
            parent = self.categories.get(data['parent'])
            cat, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={'parent': parent}
            )
            self.categories[data['name']] = cat
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {len(self.categories)} Categories'))

    def create_products(self):
        self.stdout.write('  Creating Products...')
        
        products_data = [
            # Finished goods (beverages)
            {'name': 'Espresso', 'category': 'Coffee', 'uom': 'cup', 'type': 'stockable', 'cost': 8000, 'price': 18000},
            {'name': 'Americano', 'category': 'Coffee', 'uom': 'cup', 'type': 'stockable', 'cost': 10000, 'price': 22000},
            {'name': 'Cappuccino', 'category': 'Coffee', 'uom': 'cup', 'type': 'stockable', 'cost': 12000, 'price': 28000},
            {'name': 'Caffe Latte', 'category': 'Coffee', 'uom': 'cup', 'type': 'stockable', 'cost': 12000, 'price': 28000},
            {'name': 'Mocha', 'category': 'Coffee', 'uom': 'cup', 'type': 'stockable', 'cost': 14000, 'price': 32000},
            {'name': 'Caramel Macchiato', 'category': 'Coffee', 'uom': 'cup', 'type': 'stockable', 'cost': 15000, 'price': 35000},
            {'name': 'Matcha Latte', 'category': 'Non-Coffee', 'uom': 'cup', 'type': 'stockable', 'cost': 14000, 'price': 30000},
            {'name': 'Chocolate', 'category': 'Non-Coffee', 'uom': 'cup', 'type': 'stockable', 'cost': 12000, 'price': 25000},
            {'name': 'Green Tea', 'category': 'Non-Coffee', 'uom': 'cup', 'type': 'stockable', 'cost': 8000, 'price': 18000},
            
            # Food
            {'name': 'Croissant', 'category': 'Pastry', 'uom': 'pcs', 'type': 'stockable', 'cost': 12000, 'price': 25000},
            {'name': 'Danish Pastry', 'category': 'Pastry', 'uom': 'pcs', 'type': 'stockable', 'cost': 10000, 'price': 22000},
            {'name': 'Cheesecake', 'category': 'Cake', 'uom': 'pcs', 'type': 'stockable', 'cost': 20000, 'price': 45000},
            {'name': 'Tiramisu', 'category': 'Cake', 'uom': 'pcs', 'type': 'stockable', 'cost': 22000, 'price': 48000},
            
            # Raw Materials
            {'name': 'Coffee Beans (Arabica)', 'category': 'Raw Materials', 'uom': 'kg', 'type': 'stockable', 'cost': 180000, 'price': 0, 'can_be_sold': False},
            {'name': 'Coffee Beans (Robusta)', 'category': 'Raw Materials', 'uom': 'kg', 'type': 'stockable', 'cost': 120000, 'price': 0, 'can_be_sold': False},
            {'name': 'Fresh Milk', 'category': 'Raw Materials', 'uom': 'L', 'type': 'stockable', 'cost': 18000, 'price': 0, 'can_be_sold': False},
            {'name': 'Matcha Powder', 'category': 'Raw Materials', 'uom': 'kg', 'type': 'stockable', 'cost': 350000, 'price': 0, 'can_be_sold': False},
            {'name': 'Chocolate Powder', 'category': 'Raw Materials', 'uom': 'kg', 'type': 'stockable', 'cost': 85000, 'price': 0, 'can_be_sold': False},
            {'name': 'Sugar', 'category': 'Raw Materials', 'uom': 'kg', 'type': 'stockable', 'cost': 14000, 'price': 0, 'can_be_sold': False},
            {'name': 'Caramel Syrup', 'category': 'Raw Materials', 'uom': 'L', 'type': 'stockable', 'cost': 65000, 'price': 0, 'can_be_sold': False},
            {'name': 'Vanilla Syrup', 'category': 'Raw Materials', 'uom': 'L', 'type': 'stockable', 'cost': 60000, 'price': 0, 'can_be_sold': False},
            
            # Packaging
            {'name': 'Paper Cup 8oz', 'category': 'Packaging', 'uom': 'pcs', 'type': 'stockable', 'cost': 800, 'price': 0, 'can_be_sold': False},
            {'name': 'Paper Cup 12oz', 'category': 'Packaging', 'uom': 'pcs', 'type': 'stockable', 'cost': 1000, 'price': 0, 'can_be_sold': False},
            {'name': 'Cup Lid', 'category': 'Packaging', 'uom': 'pcs', 'type': 'stockable', 'cost': 300, 'price': 0, 'can_be_sold': False},
            {'name': 'Paper Bag', 'category': 'Packaging', 'uom': 'pcs', 'type': 'stockable', 'cost': 500, 'price': 0, 'can_be_sold': False},
            {'name': 'Straw', 'category': 'Packaging', 'uom': 'pcs', 'type': 'stockable', 'cost': 150, 'price': 0, 'can_be_sold': False},
        ]
        
        self.products = {}
        for data in products_data:
            product, created = Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'category': self.categories.get(data['category']),
                    'uom': self.uoms.get(data['uom']),
                    'product_type': data.get('type', 'stockable'),
                    'standard_price': Decimal(str(data['cost'])),
                    'list_price': Decimal(str(data['price'])),
                    'can_be_sold': data.get('can_be_sold', True),
                    'can_be_purchased': True,
                }
            )
            self.products[data['name']] = product
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {len(products_data)} Products'))

    def create_vendors(self):
        self.stdout.write('  Creating Vendors...')
        
        vendors_data = [
            {
                'name': 'PT Kopi Nusantara',
                'code': 'KN001',
                'email': 'sales@kopinusantara.co.id',
                'phone': '021-5551234',
                'street': 'Jl. Kopi Raya No. 123',
                'city': 'Jakarta Selatan',
                'products': ['Coffee Beans (Arabica)', 'Coffee Beans (Robusta)']
            },
            {
                'name': 'CV Susu Segar Makmur',
                'code': 'SSM01',
                'email': 'order@sususegar.com',
                'phone': '021-5559876',
                'street': 'Jl. Peternakan No. 45',
                'city': 'Bandung',
                'products': ['Fresh Milk']
            },
            {
                'name': 'PT Indo Packaging',
                'code': 'IP001',
                'email': 'sales@indopack.co.id',
                'phone': '021-5557890',
                'street': 'Kawasan Industri Pulogadung',
                'city': 'Jakarta Timur',
                'products': ['Paper Cup 8oz', 'Paper Cup 12oz', 'Cup Lid', 'Paper Bag', 'Straw']
            },
            {
                'name': 'Toko Bahan Kue Sentosa',
                'code': 'BKS01',
                'email': 'sentosa.baking@gmail.com',
                'phone': '021-5554567',
                'street': 'Jl. Pasar Baru No. 78',
                'city': 'Jakarta Pusat',
                'products': ['Sugar', 'Chocolate Powder', 'Caramel Syrup', 'Vanilla Syrup', 'Matcha Powder']
            },
        ]
        
        self.vendors = {}
        for data in vendors_data:
            vendor, created = Vendor.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'street': data['street'],
                    'city': data['city'],
                }
            )
            self.vendors[data['name']] = vendor
            
            # Create vendor contacts
            if created:
                VendorContact.objects.create(
                    vendor=vendor,
                    name=f"Sales {data['name'].split()[0]}",
                    email=data['email'],
                    phone=data['phone'],
                    is_primary=True
                )
            
            # Link products to vendor
            for prod_name in data['products']:
                product = self.products.get(prod_name)
                if product:
                    VendorProduct.objects.get_or_create(
                        vendor=vendor,
                        product=product,
                        defaults={'price': product.standard_price}
                    )
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {len(vendors_data)} Vendors'))

    def create_warehouses(self):
        self.stdout.write('  Creating Warehouses & Locations...')
        
        # Main warehouse
        self.warehouse, _ = Warehouse.objects.get_or_create(
            code='WH-MAIN',
            defaults={
                'name': 'Main Warehouse',
                'address': 'Jl. Cafe Utama No. 1, Jakarta'
            }
        )
        
        # Locations
        locations_data = [
            {'name': 'Stock Room', 'code': 'WH/STOCK', 'type': 'internal'},
            {'name': 'Kitchen', 'code': 'WH/KITCHEN', 'type': 'internal'},
            {'name': 'Bar Counter', 'code': 'WH/BAR', 'type': 'internal'},
            {'name': 'Receiving Area', 'code': 'WH/RECEIVE', 'type': 'internal'},
            {'name': 'Vendor Location', 'code': 'VENDOR', 'type': 'supplier'},
            {'name': 'Customer Location', 'code': 'CUSTOMER', 'type': 'customer'},
        ]
        
        self.locations = {}
        for data in locations_data:
            loc, _ = Location.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'warehouse': self.warehouse if data['type'] == 'internal' else None,
                    'location_type': data['type']
                }
            )
            self.locations[data['code']] = loc
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ 1 Warehouse, {len(locations_data)} Locations'))

    def create_stock(self):
        self.stdout.write('  Creating Initial Stock...')
        
        stock_location = self.locations.get('WH/STOCK')
        
        stock_data = {
            'Coffee Beans (Arabica)': 50,
            'Coffee Beans (Robusta)': 30,
            'Fresh Milk': 100,
            'Matcha Powder': 5,
            'Chocolate Powder': 10,
            'Sugar': 25,
            'Caramel Syrup': 8,
            'Vanilla Syrup': 8,
            'Paper Cup 8oz': 500,
            'Paper Cup 12oz': 500,
            'Cup Lid': 1000,
            'Paper Bag': 300,
            'Straw': 1000,
            'Croissant': 20,
            'Danish Pastry': 15,
            'Cheesecake': 10,
            'Tiramisu': 8,
        }
        
        count = 0
        for prod_name, qty in stock_data.items():
            product = self.products.get(prod_name)
            if product and stock_location:
                StockQuant.objects.get_or_create(
                    product=product,
                    location=stock_location,
                    defaults={'quantity': Decimal(str(qty))}
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {count} Stock entries'))

    def create_customers(self):
        self.stdout.write('  Creating Customers...')
        
        customers_data = [
            {'name': 'Budi Santoso', 'type': 'individual', 'phone': '081234567890', 'email': 'budi.s@gmail.com', 'city': 'Jakarta'},
            {'name': 'Siti Rahayu', 'type': 'individual', 'phone': '082345678901', 'email': 'siti.r@gmail.com', 'city': 'Jakarta'},
            {'name': 'Ahmad Wijaya', 'type': 'individual', 'phone': '083456789012', 'email': 'ahmad.w@gmail.com', 'city': 'Tangerang'},
            {'name': 'Dewi Lestari', 'type': 'individual', 'phone': '084567890123', 'email': 'dewi.l@gmail.com', 'city': 'Bekasi'},
            {'name': 'Rudi Hermawan', 'type': 'individual', 'phone': '085678901234', 'email': 'rudi.h@gmail.com', 'city': 'Depok'},
            {'name': 'PT Teknologi Maju', 'type': 'company', 'phone': '021-7891234', 'email': 'office@teknologimaju.co.id', 'city': 'Jakarta', 'company': 'PT Teknologi Maju', 'tax_id': '01.234.567.8-012.000'},
            {'name': 'CV Berkah Jaya', 'type': 'company', 'phone': '021-7892345', 'email': 'admin@berkahjaya.com', 'city': 'Jakarta', 'company': 'CV Berkah Jaya', 'tax_id': '02.345.678.9-023.000'},
            {'name': 'Startup Hub Indonesia', 'type': 'company', 'phone': '021-7893456', 'email': 'hello@startuphub.id', 'city': 'Jakarta', 'company': 'PT Startup Hub Indonesia'},
        ]
        
        self.customers = {}
        for data in customers_data:
            customer, _ = Customer.objects.get_or_create(
                email=data['email'],
                defaults={
                    'name': data['name'],
                    'customer_type': data['type'],
                    'phone': data['phone'],
                    'city': data['city'],
                    'company_name': data.get('company', ''),
                    'tax_id': data.get('tax_id', ''),
                }
            )
            self.customers[data['name']] = customer
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {len(customers_data)} Customers'))

    def create_bom(self):
        self.stdout.write('  Creating Bill of Materials...')
        
        bom_data = [
            {
                'product': 'Cappuccino',
                'qty': 1,
                'components': [
                    ('Coffee Beans (Arabica)', Decimal('0.02')),  # 20g per cup
                    ('Fresh Milk', Decimal('0.15')),  # 150ml
                    ('Paper Cup 12oz', Decimal('1')),
                    ('Cup Lid', Decimal('1')),
                ]
            },
            {
                'product': 'Caffe Latte',
                'qty': 1,
                'components': [
                    ('Coffee Beans (Arabica)', Decimal('0.02')),
                    ('Fresh Milk', Decimal('0.2')),  # More milk
                    ('Paper Cup 12oz', Decimal('1')),
                    ('Cup Lid', Decimal('1')),
                ]
            },
            {
                'product': 'Mocha',
                'qty': 1,
                'components': [
                    ('Coffee Beans (Arabica)', Decimal('0.02')),
                    ('Fresh Milk', Decimal('0.15')),
                    ('Chocolate Powder', Decimal('0.015')),
                    ('Paper Cup 12oz', Decimal('1')),
                    ('Cup Lid', Decimal('1')),
                ]
            },
            {
                'product': 'Caramel Macchiato',
                'qty': 1,
                'components': [
                    ('Coffee Beans (Arabica)', Decimal('0.02')),
                    ('Fresh Milk', Decimal('0.18')),
                    ('Caramel Syrup', Decimal('0.02')),
                    ('Vanilla Syrup', Decimal('0.01')),
                    ('Paper Cup 12oz', Decimal('1')),
                    ('Cup Lid', Decimal('1')),
                ]
            },
            {
                'product': 'Matcha Latte',
                'qty': 1,
                'components': [
                    ('Matcha Powder', Decimal('0.005')),
                    ('Fresh Milk', Decimal('0.2')),
                    ('Sugar', Decimal('0.01')),
                    ('Paper Cup 12oz', Decimal('1')),
                    ('Cup Lid', Decimal('1')),
                ]
            },
            {
                'product': 'Chocolate',
                'qty': 1,
                'components': [
                    ('Chocolate Powder', Decimal('0.025')),
                    ('Fresh Milk', Decimal('0.2')),
                    ('Sugar', Decimal('0.01')),
                    ('Paper Cup 12oz', Decimal('1')),
                    ('Cup Lid', Decimal('1')),
                ]
            },
            {
                'product': 'Americano',
                'qty': 1,
                'components': [
                    ('Coffee Beans (Arabica)', Decimal('0.02')),
                    ('Paper Cup 8oz', Decimal('1')),
                    ('Cup Lid', Decimal('1')),
                ]
            },
            {
                'product': 'Espresso',
                'qty': 1,
                'components': [
                    ('Coffee Beans (Arabica)', Decimal('0.018')),
                    ('Paper Cup 8oz', Decimal('1')),
                ]
            },
        ]
        
        count = 0
        for data in bom_data:
            product = self.products.get(data['product'])
            if product:
                bom, created = BillOfMaterials.objects.get_or_create(
                    product=product,
                    defaults={'quantity': data['qty']}
                )
                
                if created:
                    for comp_name, comp_qty in data['components']:
                        component = self.products.get(comp_name)
                        if component:
                            BOMLine.objects.create(
                                bom=bom,
                                product=component,
                                quantity=comp_qty
                            )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {count} BOMs'))

    def create_rfq_and_po(self):
        self.stdout.write('  Creating RFQs & Purchase Orders...')
        
        # Create some RFQs
        vendor_kopi = self.vendors.get('PT Kopi Nusantara')
        vendor_pack = self.vendors.get('PT Indo Packaging')
        
        if vendor_kopi:
            rfq1, created = RequestForQuotation.objects.get_or_create(
                reference='RFQ-00001',
                defaults={
                    'vendor': vendor_kopi,
                    'state': 'received',
                }
            )
            if created:
                RFQLine.objects.create(
                    rfq=rfq1,
                    product=self.products.get('Coffee Beans (Arabica)'),
                    quantity=Decimal('25'),
                    unit_price=Decimal('180000')
                )
                RFQLine.objects.create(
                    rfq=rfq1,
                    product=self.products.get('Coffee Beans (Robusta)'),
                    quantity=Decimal('15'),
                    unit_price=Decimal('120000')
                )
        
        if vendor_pack:
            # Create a PO
            po1, created = PurchaseOrder.objects.get_or_create(
                reference='PO-00001',
                defaults={
                    'vendor': vendor_pack,
                    'state': 'received',
                    'delivery_location': self.locations.get('WH/RECEIVE'),
                }
            )
            if created:
                POLine.objects.create(
                    purchase_order=po1,
                    product=self.products.get('Paper Cup 12oz'),
                    quantity=Decimal('500'),
                    quantity_received=Decimal('500'),
                    unit_price=Decimal('1000')
                )
                POLine.objects.create(
                    purchase_order=po1,
                    product=self.products.get('Cup Lid'),
                    quantity=Decimal('500'),
                    quantity_received=Decimal('500'),
                    unit_price=Decimal('300')
                )
            
            # Another PO - draft
            po2, created = PurchaseOrder.objects.get_or_create(
                reference='PO-00002',
                defaults={
                    'vendor': vendor_pack,
                    'state': 'draft',
                }
            )
            if created:
                POLine.objects.create(
                    purchase_order=po2,
                    product=self.products.get('Paper Bag'),
                    quantity=Decimal('200'),
                    unit_price=Decimal('500')
                )
                POLine.objects.create(
                    purchase_order=po2,
                    product=self.products.get('Straw'),
                    quantity=Decimal('500'),
                    unit_price=Decimal('150')
                )
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ RFQs & POs created'))

    def create_quotations_and_orders(self):
        self.stdout.write('  Creating Sales Quotations, Orders & Invoices...')
        
        today = timezone.now().date()
        
        # Customer orders
        customer1 = self.customers.get('PT Teknologi Maju')
        customer2 = self.customers.get('Budi Santoso')
        customer3 = self.customers.get('Siti Rahayu')
        
        # Quotation (sent)
        if customer1:
            sq1, created = SalesQuotation.objects.get_or_create(
                reference='SQ-00001',
                defaults={
                    'customer': customer1,
                    'state': 'sent',
                    'validity_date': today + timedelta(days=7),
                }
            )
            if created:
                SalesQuotationLine.objects.create(
                    quotation=sq1,
                    product=self.products.get('Cappuccino'),
                    quantity=Decimal('20'),
                    unit_price=Decimal('28000')
                )
                SalesQuotationLine.objects.create(
                    quotation=sq1,
                    product=self.products.get('Croissant'),
                    quantity=Decimal('20'),
                    unit_price=Decimal('25000')
                )
        
        # Sales Order (confirmed, processing)
        if customer2:
            so1, created = SalesOrder.objects.get_or_create(
                reference='SO-00001',
                defaults={
                    'customer': customer2,
                    'state': 'processing',
                }
            )
            if created:
                SalesOrderLine.objects.create(
                    sales_order=so1,
                    product=self.products.get('Caffe Latte'),
                    quantity=Decimal('2'),
                    unit_price=Decimal('28000')
                )
                SalesOrderLine.objects.create(
                    sales_order=so1,
                    product=self.products.get('Cheesecake'),
                    quantity=Decimal('1'),
                    unit_price=Decimal('45000')
                )
        
        # Sales Order (delivered with invoice)
        if customer3:
            so2, created = SalesOrder.objects.get_or_create(
                reference='SO-00002',
                defaults={
                    'customer': customer3,
                    'state': 'delivered',
                }
            )
            if created:
                SalesOrderLine.objects.create(
                    sales_order=so2,
                    product=self.products.get('Mocha'),
                    quantity=Decimal('1'),
                    quantity_delivered=Decimal('1'),
                    unit_price=Decimal('32000')
                )
                SalesOrderLine.objects.create(
                    sales_order=so2,
                    product=self.products.get('Tiramisu'),
                    quantity=Decimal('1'),
                    quantity_delivered=Decimal('1'),
                    unit_price=Decimal('48000')
                )
                
                # Create invoice
                inv1, inv_created = SalesInvoice.objects.get_or_create(
                    reference='INV-00001',
                    defaults={
                        'customer': customer3,
                        'sales_order': so2,
                        'state': 'paid',
                        'due_date': today,
                        'payment_date': today,
                        'payment_method': 'qris',
                        'amount_paid': Decimal('88880'),  # with tax
                    }
                )
                if inv_created:
                    SalesInvoiceLine.objects.create(
                        invoice=inv1,
                        product=self.products.get('Mocha'),
                        quantity=Decimal('1'),
                        unit_price=Decimal('32000')
                    )
                    SalesInvoiceLine.objects.create(
                        invoice=inv1,
                        product=self.products.get('Tiramisu'),
                        quantity=Decimal('1'),
                        unit_price=Decimal('48000')
                    )
        
        # Another completed order
        customer4 = self.customers.get('Ahmad Wijaya')
        if customer4:
            so3, created = SalesOrder.objects.get_or_create(
                reference='SO-00003',
                defaults={
                    'customer': customer4,
                    'state': 'done',
                }
            )
            if created:
                SalesOrderLine.objects.create(
                    sales_order=so3,
                    product=self.products.get('Americano'),
                    quantity=Decimal('2'),
                    quantity_delivered=Decimal('2'),
                    quantity_invoiced=Decimal('2'),
                    unit_price=Decimal('22000')
                )
                
                inv2, _ = SalesInvoice.objects.get_or_create(
                    reference='INV-00002',
                    defaults={
                        'customer': customer4,
                        'sales_order': so3,
                        'state': 'paid',
                        'payment_method': 'cash',
                        'amount_paid': Decimal('48840'),
                    }
                )
                if _:
                    SalesInvoiceLine.objects.create(
                        invoice=inv2,
                        product=self.products.get('Americano'),
                        quantity=Decimal('2'),
                        unit_price=Decimal('22000')
                    )
        
        # Draft order
        customer5 = self.customers.get('Startup Hub Indonesia')
        if customer5:
            so4, created = SalesOrder.objects.get_or_create(
                reference='SO-00004',
                defaults={
                    'customer': customer5,
                    'state': 'draft',
                }
            )
            if created:
                SalesOrderLine.objects.create(
                    sales_order=so4,
                    product=self.products.get('Caramel Macchiato'),
                    quantity=Decimal('15'),
                    unit_price=Decimal('35000')
                )
                SalesOrderLine.objects.create(
                    sales_order=so4,
                    product=self.products.get('Matcha Latte'),
                    quantity=Decimal('10'),
                    unit_price=Decimal('30000')
                )
                SalesOrderLine.objects.create(
                    sales_order=so4,
                    product=self.products.get('Danish Pastry'),
                    quantity=Decimal('25'),
                    unit_price=Decimal('22000')
                )
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ Sales data created'))

