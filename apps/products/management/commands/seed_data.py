from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
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
    help = 'Seed database with Coffee O ERP data based on PPT (Fixed Materials)'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding database with Coffee O data...\n')
        
        try:
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
            
            self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully with Fixed Coffee O data!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error seeding database: {str(e)}'))
            raise CommandError(f'Seeding failed: {str(e)}')

    def create_uom(self):
        self.stdout.write('  Creating Units of Measure...')
        
        uoms_data = [
            {'name': 'Piece', 'symbol': 'pcs', 'category': 'unit', 'is_base_unit': True, 'ratio': Decimal('1.000000')},
            {'name': 'Kilogram', 'symbol': 'kg', 'category': 'weight', 'is_base_unit': True, 'ratio': Decimal('1.000000')},
            {'name': 'Gram', 'symbol': 'g', 'category': 'weight', 'ratio': Decimal('0.001')},
            {'name': 'Liter', 'symbol': 'L', 'category': 'volume', 'is_base_unit': True, 'ratio': Decimal('1.000000')},
            {'name': 'Milliliter', 'symbol': 'ml', 'category': 'volume', 'ratio': Decimal('0.001')},
            {'name': 'Centimeter', 'symbol': 'cm', 'category': 'length', 'is_base_unit': True, 'ratio': Decimal('1.000000')}, # Added for Tape
            {'name': 'Pack', 'symbol': 'pack', 'category': 'unit', 'ratio': Decimal('1.000000')},
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
            {'name': 'Coffee O Products', 'description': 'Finished Goods from Menu'},
            {'name': 'Raw Materials', 'description': 'Main Ingredients'},
            {'name': 'Packaging & Consumables', 'description': 'Cups, Lids, Stickers, Tissues, etc.'},
        ]
        
        self.categories = {}
        for data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            self.categories[data['name']] = cat
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {len(self.categories)} Categories'))

    def create_products(self):
        self.stdout.write('  Creating Products (Based on PPT + Fixes)...')
        
        products_data = [
            # --- Finished Goods (Menu Utama) ---
            {'name': 'Kopi Hitam Klasik (Classic Black Coffee)', 'category': 'Coffee O Products', 'uom': 'pcs', 'type': 'stockable', 'cost': 8000, 'price': 15000},
            {'name': 'Es Kopi Susu Gula Aren (Iced Palm Sugar Latte)', 'category': 'Coffee O Products', 'uom': 'pcs', 'type': 'stockable', 'cost': 12000, 'price': 22000},
            {'name': 'Kopi Machiato Caramel (Salted Caramel Macchiato)', 'category': 'Coffee O Products', 'uom': 'pcs', 'type': 'stockable', 'cost': 15000, 'price': 28000},
            
            # --- Raw Materials (Bahan Baku) ---
            # Coffee Beans
            {'name': 'Biji Kopi Arabika Gayo', 'category': 'Raw Materials', 'uom': 'g', 'type': 'stockable', 'cost': 250, 'price': 0},
            {'name': 'Biji Kopi Espresso Blend', 'category': 'Raw Materials', 'uom': 'g', 'type': 'stockable', 'cost': 200, 'price': 0},
            
            # Liquids & Dairy
            {'name': 'Air Mineral', 'category': 'Raw Materials', 'uom': 'ml', 'type': 'consumable', 'cost': 2, 'price': 0},
            {'name': 'Susu UHT Full Cream', 'category': 'Raw Materials', 'uom': 'ml', 'type': 'stockable', 'cost': 18, 'price': 0},
            {'name': 'Whipped Cream', 'category': 'Raw Materials', 'uom': 'g', 'type': 'stockable', 'cost': 80, 'price': 0},
            
            # Sweeteners & Flavorings
            {'name': 'Gula Aren Sachet', 'category': 'Raw Materials', 'uom': 'pcs', 'type': 'stockable', 'cost': 500, 'price': 0},
            {'name': 'Sirup Gula Aren', 'category': 'Raw Materials', 'uom': 'ml', 'type': 'stockable', 'cost': 60, 'price': 0},
            {'name': 'Saus Salted Caramel', 'category': 'Raw Materials', 'uom': 'ml', 'type': 'stockable', 'cost': 100, 'price': 0},
            {'name': 'Sirup Vanila', 'category': 'Raw Materials', 'uom': 'ml', 'type': 'stockable', 'cost': 90, 'price': 0},
            
            # Ice
            {'name': 'Es Batu Kristal', 'category': 'Raw Materials', 'uom': 'g', 'type': 'stockable', 'cost': 5, 'price': 0},
            
            # --- Packaging & Consumables ---
            # Cups
            {'name': 'Paper Cup 8oz + Sleeve', 'category': 'Packaging & Consumables', 'uom': 'pcs', 'type': 'stockable', 'cost': 1200, 'price': 0},
            {'name': 'Gelas Plastik 16oz', 'category': 'Packaging & Consumables', 'uom': 'pcs', 'type': 'stockable', 'cost': 800, 'price': 0},
            
            # Lids
            {'name': 'Tutup Gelas (Lid)', 'category': 'Packaging & Consumables', 'uom': 'pcs', 'type': 'stockable', 'cost': 300, 'price': 0}, 
            {'name': 'Tutup Gelas Datar (Lid)', 'category': 'Packaging & Consumables', 'uom': 'pcs', 'type': 'stockable', 'cost': 300, 'price': 0}, 
            {'name': 'Tutup Cembung (Dome Lid)', 'category': 'Packaging & Consumables', 'uom': 'pcs', 'type': 'stockable', 'cost': 400, 'price': 0},
            
            # Accessories
            {'name': 'Pengaduk Kayu', 'category': 'Packaging & Consumables', 'uom': 'pcs', 'type': 'stockable', 'cost': 100, 'price': 0},
            {'name': 'Kertas Filter V60', 'category': 'Packaging & Consumables', 'uom': 'pcs', 'type': 'stockable', 'cost': 500, 'price': 0},
            {'name': 'Stiker Label Merek', 'category': 'Packaging & Consumables', 'uom': 'pcs', 'type': 'stockable', 'cost': 200, 'price': 0},
            {'name': 'Sedotan', 'category': 'Packaging & Consumables', 'uom': 'pcs', 'type': 'stockable', 'cost': 100, 'price': 0},
            
            # REPLACEMENTS FOR GAS/ELECTRICITY
            {'name': 'Tisu (Paper Napkin)', 'category': 'Packaging & Consumables', 'uom': 'pcs', 'type': 'consumable', 'cost': 50, 'price': 0},
            {'name': 'Lakban Segel (Sealing Tape)', 'category': 'Packaging & Consumables', 'uom': 'cm', 'type': 'consumable', 'cost': 10, 'price': 0},
        ]
        
        self.products = {}
        missing_categories = []
        missing_uoms = []
        
        for data in products_data:
            category = self.categories.get(data['category'])
            uom = self.uoms.get(data['uom'])
            
            if not category:
                missing_categories.append(data['category'])
            if not uom:
                missing_uoms.append(data['uom'])
            
            if category and uom:
                product, created = Product.objects.get_or_create(
                    name=data['name'],
                    defaults={
                        'category': category,
                        'uom': uom,
                        'product_type': data.get('type', 'stockable'),
                        'standard_price': Decimal(str(data['cost'])),
                        'list_price': Decimal(str(data['price'])),
                        'can_be_sold': data['category'] == 'Coffee O Products',
                        'can_be_purchased': data['category'] != 'Coffee O Products',
                    }
                )
                self.products[data['name']] = product
            else:
                self.stdout.write(self.style.WARNING(f"    ! Skipping product '{data['name']}' - missing category or UoM"))
        
        if missing_categories:
            self.stdout.write(self.style.WARNING(f"    ! Missing categories: {', '.join(set(missing_categories))}"))
        if missing_uoms:
            self.stdout.write(self.style.WARNING(f"    ! Missing UoMs: {', '.join(set(missing_uoms))}"))
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {len(self.products)} Products Created'))

    def create_vendors(self):
        self.stdout.write('  Creating Vendors...')
        
        vendors_data = [
            {
                'name': 'Supplier Kopi Gayo',
                'code': 'SUP-KOPI',
                'email': 'order@gayocoffee.com',
                'products': ['Biji Kopi Arabika Gayo', 'Biji Kopi Espresso Blend']
            },
            {
                'name': 'Supplier Susu & Sirup',
                'code': 'SUP-DAIRY',
                'email': 'sales@milkysyrup.com',
                'products': ['Susu UHT Full Cream', 'Sirup Gula Aren', 'Saus Salted Caramel', 'Sirup Vanila', 'Whipped Cream', 'Gula Aren Sachet']
            },
            {
                'name': 'Supplier Packaging Jaya',
                'code': 'SUP-PACK',
                'email': 'admin@packjaya.com',
                'products': ['Paper Cup 8oz + Sleeve', 'Gelas Plastik 16oz', 'Tutup Gelas (Lid)', 'Tutup Gelas Datar (Lid)', 'Tutup Cembung (Dome Lid)', 'Pengaduk Kayu', 'Sedotan', 'Kertas Filter V60', 'Stiker Label Merek', 'Tisu (Paper Napkin)', 'Lakban Segel (Sealing Tape)']
            },
            {
                'name': 'Agen Es Kristal',
                'code': 'SUP-ICE',
                'email': 'agen@ice.com',
                'products': ['Es Batu Kristal']
            }
        ]
        
        self.vendors = {}
        for data in vendors_data:
            vendor, created = Vendor.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'email': data['email'],
                    'phone': '021-5550000',
                    'street': 'Jl. Vendor No. 1',
                    'city': 'Jakarta',
                }
            )
            self.vendors[data['name']] = vendor
            
            if created:
                VendorContact.objects.create(
                    vendor=vendor,
                    name=f"Admin {data['name']}",
                    email=data['email'],
                    is_primary=True
                )
            
            missing_products = []
            for prod_name in data['products']:
                product = self.products.get(prod_name)
                if product:
                    VendorProduct.objects.get_or_create(
                        vendor=vendor,
                        product=product,
                        defaults={'price': product.standard_price}
                    )
                else:
                    missing_products.append(prod_name)
            
            if missing_products:
                self.stdout.write(self.style.WARNING(f"    ! Vendor '{data['name']}' - missing products: {', '.join(missing_products)}"))
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {len(vendors_data)} Vendors'))

    def create_warehouses(self):
        self.stdout.write('  Creating Warehouses...')
        self.warehouse, _ = Warehouse.objects.get_or_create(
            code='WH-COFFEEO',
            defaults={'name': 'Coffee O Main Warehouse', 'address': 'Jl. Coffee O No. 1'}
        )
        
        locations_data = [
            {'name': 'Stock Room', 'code': 'WH/STOCK', 'type': 'internal'},
            {'name': 'Bar Station', 'code': 'WH/BAR', 'type': 'internal'},
            {'name': 'Receiving', 'code': 'WH/IN', 'type': 'internal'},
        ]
        
        self.locations = {}
        for data in locations_data:
            loc, _ = Location.objects.get_or_create(
                code=data['code'],
                warehouse=self.warehouse,  # Explicit filter to prevent conflicts
                defaults={
                    'name': data['name'],
                    'warehouse': self.warehouse,
                    'location_type': data['type']
                }
            )
            self.locations[data['code']] = loc
            
        self.stdout.write(self.style.SUCCESS(f'    ✓ Warehouse & {len(self.locations)} Locations'))

    def create_stock(self):
        self.stdout.write('  Creating Initial Stock...')
        stock_loc = self.locations.get('WH/STOCK')
        
        if not stock_loc:
            self.stdout.write(self.style.ERROR('    ✗ Stock location not found!'))
            return
        
        initial_stock = {
            'Biji Kopi Arabika Gayo': 10000,
            'Biji Kopi Espresso Blend': 10000,
            'Susu UHT Full Cream': 50000,
            'Sirup Gula Aren': 5000,
            'Gelas Plastik 16oz': 500,
            'Paper Cup 8oz + Sleeve': 500,
            'Stiker Label Merek': 1000,
            'Tisu (Paper Napkin)': 2000,
            'Lakban Segel (Sealing Tape)': 5000,
        }
        
        created_count = 0
        missing_products = []
        
        for name, qty in initial_stock.items():
            product = self.products.get(name)
            if product and stock_loc:
                quant, created = StockQuant.objects.get_or_create(
                    product=product,
                    location=stock_loc,
                    defaults={
                        'quantity': Decimal(str(qty)),
                        'unit_cost': product.standard_price  # Use product cost for accurate valuation
                    }
                )
                if created:
                    created_count += 1
            elif not product:
                missing_products.append(name)
        
        if missing_products:
            self.stdout.write(self.style.WARNING(f"    ! Missing products for stock: {', '.join(missing_products)}"))
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {created_count} Stock Items Initialized'))

    def create_customers(self):
        self.stdout.write('  Creating Customers...')
        customers = ['Pelanggan Walk-in', 'Gojek Driver', 'Grab Driver']
        self.customers = {}
        for name in customers:
            cust, _ = Customer.objects.get_or_create(
                name=name,
                defaults={'customer_type': 'individual', 'email': f'{name.lower().replace(" ", "")}@example.com'}
            )
            self.customers[name] = cust
        self.stdout.write(self.style.SUCCESS(f'    ✓ Customers Created'))

    def create_bom(self):
        self.stdout.write('  Creating Bill of Materials (10 items rule)...')
        
        # BOM adjusted to replace Gas/Electricity with Tisu/Tape
        bom_recipes = [
            {
                'product': 'Kopi Hitam Klasik (Classic Black Coffee)',
                'qty': 1,
                'components': [
                    ('Biji Kopi Arabika Gayo', 15),     # 1
                    ('Air Mineral', 220),               # 2
                    ('Gula Aren Sachet', 1),            # 3
                    ('Paper Cup 8oz + Sleeve', 1),      # 4
                    ('Tutup Gelas (Lid)', 1),           # 5
                    ('Pengaduk Kayu', 1),               # 6
                    ('Kertas Filter V60', 1),           # 7
                    ('Stiker Label Merek', 1),          # 8
                    ('Tisu (Paper Napkin)', 1),         # 9 (Replaces Gas)
                    ('Lakban Segel (Sealing Tape)', 5), # 10 (Replaces Electricity, 5cm)
                ]
            },
            {
                'product': 'Es Kopi Susu Gula Aren (Iced Palm Sugar Latte)',
                'qty': 1,
                'components': [
                    ('Biji Kopi Espresso Blend', 18),   # 1
                    ('Susu UHT Full Cream', 120),       # 2
                    ('Sirup Gula Aren', 20),            # 3
                    ('Es Batu Kristal', 100),           # 4
                    ('Air Mineral', 40),                # 5
                    ('Gelas Plastik 16oz', 1),          # 6
                    ('Tutup Gelas Datar (Lid)', 1),     # 7
                    ('Sedotan', 1),                     # 8
                    ('Stiker Label Merek', 1),          # 9
                    ('Tisu (Paper Napkin)', 1),         # 10 (Replaces Electricity)
                ]
            },
            {
                'product': 'Kopi Machiato Caramel (Salted Caramel Macchiato)',
                'qty': 1,
                'components': [
                    ('Biji Kopi Espresso Blend', 18),   # 1
                    ('Susu UHT Full Cream', 150),       # 2
                    ('Saus Salted Caramel', 25),        # 3
                    ('Sirup Vanila', 10),               # 4
                    ('Es Batu Kristal', 80),            # 5
                    ('Air Mineral', 40),                # 6
                    ('Gelas Plastik 16oz', 1),          # 7
                    ('Tutup Cembung (Dome Lid)', 1),    # 8
                    ('Sedotan', 1),                     # 9
                    ('Stiker Label Merek', 1),          # 10
                    ('Tisu (Paper Napkin)', 1),         # 11 (Replaces Electricity)
                    ('Whipped Cream', 20),              # 12
                ]
            }
        ]
        
        bom_count = 0
        component_count = 0
        
        for recipe in bom_recipes:
            main_product = self.products.get(recipe['product'])
            if not main_product:
                self.stdout.write(self.style.WARNING(f"    ! Product not found: {recipe['product']}"))
                continue
            
            bom, created = BillOfMaterials.objects.get_or_create(
                product=main_product,
                defaults={'quantity': recipe['qty']}
            )
            
            # Check if BOM needs components (new or empty)
            needs_components = created or not bom.lines.exists()
            
            if created:
                self.stdout.write(f"    - Creating BOM for {recipe['product']}")
                bom_count += 1
            elif needs_components:
                self.stdout.write(f"    - Adding components to existing empty BOM for {recipe['product']}")
            
            if needs_components:
                missing_components = []
                for comp_name, comp_qty in recipe['components']:
                    component = self.products.get(comp_name)
                    if component:
                        line, line_created = BOMLine.objects.get_or_create(
                            bom=bom,
                            product=component,
                            defaults={'quantity': Decimal(str(comp_qty))}
                        )
                        if line_created:
                            component_count += 1
                    else:
                        missing_components.append(comp_name)
                
                if missing_components:
                    self.stdout.write(self.style.WARNING(f"      ! Missing components: {', '.join(missing_components)}"))
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ {bom_count} BOMs Created/Updated, {component_count} Components Added'))

    def create_rfq_and_po(self):
        self.stdout.write('  Creating RFQs & POs...')
        vendor = self.vendors.get('Supplier Packaging Jaya')
        delivery_loc = self.locations.get('WH/IN')
        
        if not vendor:
            self.stdout.write(self.style.WARNING('    ! Vendor not found: Supplier Packaging Jaya'))
            return
        
        if not delivery_loc:
            self.stdout.write(self.style.WARNING('    ! Delivery location not found: WH/IN'))
            return
        
        po, created = PurchaseOrder.objects.get_or_create(
            reference='PO-PACK-001',
            defaults={
                'vendor': vendor, 
                'state': 'confirmed',  # Start with confirmed, will be received after line creation
                'delivery_location': delivery_loc
            }
        )
        
        if created:
            product = self.products.get('Tisu (Paper Napkin)')
            if product:
                POLine.objects.create(
                    purchase_order=po, 
                    product=product, 
                    quantity=1000, 
                    quantity_received=1000, 
                    unit_price=50
                )
                # Update PO state to received since quantity_received = quantity
                po.state = 'received'
                po.save(update_fields=['state'])
                self.stdout.write(self.style.SUCCESS('    ✓ Purchase Order created with received state'))
            else:
                self.stdout.write(self.style.WARNING('    ! Product not found: Tisu (Paper Napkin)'))
        else:
            self.stdout.write('    - Purchase Order already exists')
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ Purchase Data Created'))

    def create_quotations_and_orders(self):
        self.stdout.write('  Creating Sales Orders...')
        cust = self.customers.get('Pelanggan Walk-in')
        prod = self.products.get('Es Kopi Susu Gula Aren (Iced Palm Sugar Latte)')
        
        if not cust:
            self.stdout.write(self.style.WARNING('    ! Customer not found: Pelanggan Walk-in'))
            return
        
        if not prod:
            self.stdout.write(self.style.WARNING('    ! Product not found: Es Kopi Susu Gula Aren (Iced Palm Sugar Latte)'))
            return
        
        so, created = SalesOrder.objects.get_or_create(
            reference='SO-TODAY-001',
            defaults={'customer': cust, 'state': 'done'}
        )
        
        if created:
            SalesOrderLine.objects.create(
                sales_order=so,
                product=prod,
                quantity=2,
                unit_price=22000
            )
            self.stdout.write(self.style.SUCCESS('    ✓ Sales Order created'))
        else:
            self.stdout.write('    - Sales Order already exists')
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ Sales Data Created'))