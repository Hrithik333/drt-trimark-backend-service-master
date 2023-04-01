metric_type_config = {
    "1": {
        "Time Axis": "date",
        "Tax Amount": "number",
        "Product Unit Cost": "number",
        "Product Extended Cost": "number",
        "Product Landed Cost": "number",
        "Product Average Cost": "number",
        "Product Accounting Cost": "number",
        "Product PO Cost": "number",
        "Product Total Price": "number",
        "Order Quantity UOM": "number",
        "Invoice Quantity": "number",
        "Invoice Quantity UOM": "number",
        "Shipped Quantity": "number",
        "Shipped Quantity UOM": "number",
        "Backorder Quantity": "number"
    },
    "2": {
        "Time Axis": "date",
        "Recieved Quantity": "number",
        "Vouchered Quantity": "number",
        "Unit Price": "number",
        "Extended Price": "number",
        "Freight Amount": "number"
    }
}

date_selector = {"Standardized Sales Order": "order_created_date", "Standardized Purchase Order": "po_created_dt"}

use_case_id = {"Standardized Sales Order": 1, "Standardized Purchase Order": 2}
