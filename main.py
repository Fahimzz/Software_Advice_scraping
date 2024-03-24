import datetime
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import InvalidArgumentException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import time


def write_to_csv(data):
    with open('listings.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'Icon URL',
            'Number of Reviews',
            'Category 2',
            'Picture URL2',
            'Average Ratings',
            'Category 1',
            'Listing URL',
            'Picture URL3',
            'ListingName',
            'Visit Website URL',
            'About',
            'Video URL1',
            'Picture URL1',
            'Picture URL4',
            'ListingScrapeDate',
            'ListingRank',
            'ListingSellerName'
        ])
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(data)


# URL of the webpage containing the categories
main_url = "https://www.softwareadvice.com.sg/directory"
url = "https://www.softwareadvice.com.sg"
# Initialize the Chrome webdriver
options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
# options.add_argument('--headless')  # Optional: run headless if you don't want the browser window to show up
driver = webdriver.Chrome(options=options)
# Open the webpage
try:
    driver.get(main_url)
    driver.maximize_window()
except InvalidArgumentException as e:
    print("Invalid URL:", e)

get_category_tag = driver.find_element(By.ID, 'categories_list')
get_category_list = get_category_tag.find_elements(By.TAG_NAME, 'a')

for category in get_category_list[2:]:
    rank = 1
    visit_website_url = ''
    category_name = category.text
    category_url = category.get_attribute('href')
    driver.execute_script("window.open('" + category_url + "', '_blank');")
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(10)
    icon_url = ''
    product_description = ''
    get_all_first_page_article = driver.find_elements(By.CLASS_NAME, 'product__card')

    for first_article in get_all_first_page_article:
        article_html = first_article.get_attribute('outerHTML')
        soup = BeautifulSoup(article_html, 'html.parser')
        learn_more_link = soup.find('a', class_='text-underline')
        img_urls = []
        video_src = ''
        num_reviewers = ''

        if learn_more_link:
            href_value = learn_more_link.get('href')
            driver.execute_script("window.open('" + url + href_value + "', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(5)
            new_page_html = driver.page_source
            new_page_soup = BeautifulSoup(new_page_html, 'html.parser')
            img_tag = new_page_soup.find('img', class_='img-fluid product-header__logo')
            if img_tag:
                icon_url = img_tag.get('src')
            product_name = new_page_soup.find('h1', class_='m-0').text.strip()
            try:
                img_tag = new_page_soup.find('img', class_='img-fluid product-header__logo')
                if img_tag:
                    icon_url = img_tag.get('src')
            except:
                icon_url = ' '

            product_name = new_page_soup.find('h1', class_='m-0').text.strip()
            try:
                overall_rating = new_page_soup.find('span', class_='text-nowrap fw-bold').text.strip()
            except Exception as e:
                overall_rating = ''
            try:
                num_reviewers=new_page_soup.find('a', class_='text-decoration-none').text.strip()
            except Exception as e:
                num_reviewers = ''
            try:
                product_description_div = new_page_soup.find('div', id='productDescription')
                product_description = ''
                if product_description_div:
                    product_description = product_description_div.text.strip()
                    print("Product Description:", product_description)
            except:
                product_description = ''
            media_viewer_div = ''
            try:
                # Check if the mediaViewer div is available
                media_viewer_div = driver.find_element(By.ID, 'mediaViewer')

                # Check if the video URL is available
                video_frame = media_viewer_div.find_element(By.XPATH, "//div[@id='video_frame_0']//iframe")
                video_src = video_frame.get_attribute("src")
                print("Video URL:", video_src)

                # Check if the image URLs are available
                img_thumbnails = media_viewer_div.find_elements(By.CLASS_NAME, 'js-img-thumbnail')
                for img_thumbnail in img_thumbnails:
                    try:
                        img_url = img_thumbnail.find_element(By.TAG_NAME, 'img').get_attribute("src")
                        img_urls.append(img_url)
                    except Exception as e:
                        print(e.args)  # If image URL not available, continue to the next one

                print("Image URLs:", img_urls)
            except Exception as e:
                print("Media Viewer not available")
                img_thumbnails = media_viewer_div.find_elements(By.CLASS_NAME, 'js-img-thumbnail')
                for img_thumbnail in img_thumbnails:
                    try:
                        img_url = img_thumbnail.find_element(By.TAG_NAME, 'img').get_attribute("src")
                        img_urls.append(img_url)
                    except Exception as e:
                        print(e.args)  # If image URL not available, continue to the next one
                # If image URL not available, continue to the next one

                print("Image URLs:", img_urls)
            visit_website_url = driver.find_element(By.CSS_SELECTOR, "a.btn.btn-spacecadet-50").get_attribute("href")
            print("Visit Website URL:", visit_website_url)
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
            data = {
                'Icon URL': icon_url,
                'Number of Reviews': num_reviewers,
                'Category 2': product_name,
                'Picture URL2': img_urls[1] if len(img_urls) > 1 else '',
                'Average Ratings': overall_rating,
                'Category 1': category_name,
                'Listing URL': url + href_value,
                'Picture URL3': img_urls[2] if len(img_urls) > 2 else '',
                'ListingName': product_name,
                'Visit Website URL': visit_website_url,
                'About': product_description,
                'Video URL1': video_src if 'youtube' in video_src else '',
                'Picture URL1': img_urls[0] if len(img_urls) > 0 else '',
                'Picture URL4': img_urls[3] if len(img_urls) > 3 else '',
                'ListingScrapeDate': datetime.datetime.now().strftime("%Y-%m-%d"),
                'ListingRank': f'{category_name} - {rank}',
                'ListingSellerName': ''
            }
            write_to_csv(data)
            print(href_value)
        rank += 1

    try:
        pagination_div = driver.find_element(By.CLASS_NAME, 'pagination-container')
        pagination_li = pagination_div.find_elements(By.TAG_NAME, 'li')
        page_numbers = [int(li.text) for li in pagination_li if li.text.isdigit()]
        # Find the maximum page number
        max_page_number = max(page_numbers)

        for i in range(2, max_page_number + 1):
            page_url = category_url + f'?page={i}'
            driver.execute_script("window.open('" + page_url + "', '_blank');")
            time.sleep(4)
            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])
            get_all_next_page_article = driver.find_elements(By.CLASS_NAME, 'product__card')
            for next_article in get_all_next_page_article:
                img_urls = []
                video_src = ''
                visit_website_url = ''
                num_reviewers = ''
                product_description = ''
                article_html = next_article.get_attribute('outerHTML')
                soup = BeautifulSoup(article_html, 'html.parser')
                learn_more_link = soup.find('a', class_='text-underline')
                if learn_more_link:
                    href_value = learn_more_link.get('href')
                    driver.execute_script("window.open('" + url + href_value + "', '_blank');")
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(5)
                    new_page_html = driver.page_source
                    new_page_soup = BeautifulSoup(new_page_html, 'html.parser')
                    try:
                        img_tag = new_page_soup.find('img', class_='img-fluid product-header__logo')
                        if img_tag:
                            icon_url = img_tag.get('src')
                    except:
                        icon_url = ' '

                    product_name = new_page_soup.find('h1', class_='m-0').text.strip()
                    try:
                        overall_rating = new_page_soup.find('span', class_='text-nowrap fw-bold').text.strip()
                    except Exception as e:
                        overall_rating = ''
                    try:
                        num_reviewers=new_page_soup.find('a', class_='text-decoration-none').text.strip()
                    except Exception as e:
                        num_reviewers = ''
                    try:
                        product_description_div = new_page_soup.find('div', id='productDescription')
                        product_description = ''
                        if product_description_div:
                            product_description = product_description_div.text.strip()
                            print("Product Description:", product_description)
                    except:
                        product_description = ''

                    media_viewer_div = ''
                    try:
                        # Check if the mediaViewer div is available
                        media_viewer_div = driver.find_element(By.ID, 'mediaViewer')

                        # Check if the video URL is available
                        video_frame = media_viewer_div.find_element(By.XPATH, "//div[@id='video_frame_0']//iframe")
                        video_src = video_frame.get_attribute("src")
                        print("Video URL:", video_src)

                        # Check if the image URLs are available
                        img_thumbnails = media_viewer_div.find_elements(By.CLASS_NAME, 'js-img-thumbnail')
                        for img_thumbnail in img_thumbnails:
                            try:
                                img_url = img_thumbnail.find_element(By.TAG_NAME, 'img').get_attribute("src")
                                img_urls.append(img_url)
                            except Exception as e:
                                print(e.args)  # If image URL not available, continue to the next one
                        # If image URL not available, continue to the next one

                        print("Image URLs:", img_urls)
                    except Exception as e:
                        print("Media Viewer not available")
                        img_thumbnails = media_viewer_div.find_elements(By.CLASS_NAME, 'js-img-thumbnail')
                        for img_thumbnail in img_thumbnails:
                            try:
                                img_url = img_thumbnail.find_element(By.TAG_NAME, 'img').get_attribute("src")
                                img_urls.append(img_url)
                            except Exception as e:
                                print(e.args)  # If image URL not available, continue to the next one
                        # If image URL not available, continue to the next one

                        print("Image URLs:", img_urls)
                    visit_website_url = driver.find_element(By.CSS_SELECTOR, "a.btn.btn-spacecadet-50").get_attribute(
                        "href")
                    print("Visit Website URL:", visit_website_url)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[-1])
                    data = {
                        'Icon URL': icon_url,
                        'Number of Reviews': num_reviewers,
                        'Category 2': product_name,
                        'Picture URL2': img_urls[1] if len(img_urls) > 1 else '',
                        'Average Ratings': overall_rating,
                        'Category 1': category_name,
                        'Listing URL': url + href_value,
                        'Picture URL3': img_urls[2] if len(img_urls) > 2 else '',
                        'ListingName': product_name,
                        'Visit Website URL': visit_website_url,
                        'About': product_description,
                        'Video URL1': video_src if 'youtube' in video_src else '',
                        'Picture URL1': img_urls[0] if len(img_urls) > 0 else '',
                        'Picture URL4': img_urls[3] if len(img_urls) > 3 else '',
                        'ListingScrapeDate': datetime.datetime.now().strftime("%Y-%m-%d"),
                        'ListingRank': f'{category_name} - {rank}',
                        'ListingSellerName': ''
                    }
                    write_to_csv(data)
                    print(href_value)
                rank += 1
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
    except Exception as e:
        print(e.args)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

time.sleep(5)
driver.quit()
