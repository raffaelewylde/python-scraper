import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.learnenough.com/")
    page.get_by_role("link", name="Log In").nth(1).click()
    page.get_by_label("Email or Username").click()
    page.get_by_label("Email or Username").fill("learn@truenorthgnomes.info")
    page.locator("#user_password").click()
    page.locator("#user_password").fill("ham8yhm!RXJ3xqm2enc")
    page.get_by_role("button", name="Log In", exact=True).click()
    page.get_by_text("HTML", exact=True).click()
    page.get_by_role("link", name="Go to course").click()
    page.get_by_role("link", name="START COURSE").click()
    page.locator("#vjs_video_3_html5_api").click()
    page.locator("#vjs_video_3_html5_api").click()
    page.locator("div").filter(has_text="Pin Video Pop Out To view").nth(2).click()
    page.locator("div").filter(has_text="Pin Video Pop Out To view").nth(2).click(button="right")
    page.locator("div").filter(has_text="Pin Video Pop Out To view").nth(2).click(button="right")
    page1 = context.new_page()
    page1.goto("https://www.learnenough.com/course/learn_enough_html/html_intro?start_course=true")
    page1.close()
    page.get_by_role("img", name="images/figures/").click()
    page.get_by_role("link", name="START CHAPTER").click()
    page.get_by_role("img", name="images/figures/tim_berners-lee").click()
    page.get_by_role("img", name="images/figures/camel").click()
    page.get_by_role("link", name="NEXT: 1.2 HTML tags").click()
    page.get_by_role("link", name="Your Courses").first.click()
    page.get_by_role("link", name="Courses Guide").click()
    page.locator(".modal_content > .modal_close").click()
    page.get_by_role("link", name="Go to course").click()
    page.get_by_role("link", name="START COURSE").click()
    page.locator("#vjs_video_3_html5_api").click()
    with page.expect_popup() as page2_info:
        page.get_by_role("link", name="in-browser coding tutorials").click()
    page2 = page2_info.value
    with page.expect_popup() as page3_info:
        page.get_by_role("link", name="narrative introduction").click()
    page3 = page3_info.value
    page2.close()
    page.get_by_role("link", name="START CHAPTER").click()
    page.locator("#vjs_video_3_html5_api").click()
    page.goto("https://www.learnenough.com/course/javascript/hello_world/introduction_to_javascript?start_chapter=true")
    page.locator("#vjs_video_3_html5_api").click()
    page.locator("#vjs_video_3_html5_api").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

