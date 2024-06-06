from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import re

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=3,
    )
    open_robot_order_website()
    orders = get_orders()
    close_annoying_modal()
    fill_the_form(orders)
    archive_receipts()

def open_robot_order_website():
    # TODO: Implement your function here
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv(
    "orders.csv")
    return orders

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def fill_the_form(orders):
    page = browser.page()
    for row in orders:
        page.select_option("id=head", row["Head"])
        page.click(f"id=id-body-{row['Body']}")
        page.fill('input[placeholder="Enter the part number for the legs"]', row["Legs"])
        page.fill("id=address", row["Address"])
        page.click("id=order")
        check_for_error()
        store_receipt_as_pdf(row['Order number'])
        screenshot_robot(row['Order number'])
        page.click("id=order-another")
        close_annoying_modal()

def check_for_error():
    page = browser.page()
    if page.locator("id=order-another").is_visible():
        pass
    elif None != re.search(r"\w*", page.locator('xpath=//*[@id="root"]/div/div[1]/div/div[1]/div').inner_text()):
        page.click("id=order")
        if page.locator("id=order-another").is_visible():
            pass
        else:
            page.click("id=order")

#//*[@id="root"]/div/div[1]/div/div[1]/div


def screenshot_robot(order_number):
    page = browser.page()
    page.locator("id=robot-preview-image").screenshot(path=f"output/robo_pic_order_number_{order_number}.png")
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path=f"output/robo_pic_order_number_{order_number}.png",
        source_path=f"output/receipt/robot_receipt_{order_number}.pdf",
        output_path=f"output/receipt/robot_receipt_{order_number}.pdf"
    )

def store_receipt_as_pdf(order_number):
    page = browser.page()
    sales_results_html = page.locator("id=receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, f"output/receipt/robot_receipt_{order_number}.pdf")

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output/receipt', 'robottasks.zip', include='*.pdf')