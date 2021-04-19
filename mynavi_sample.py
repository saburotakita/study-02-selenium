import datetime
import os
import selenium
from selenium.webdriver import Chrome
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager


################# 自作関数 ######################
def write_log_file(message):
    """ ログファイルへの記述をする """
    log_file_path = "test.log"
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(log_file_path, mode="a") as f:
        f.write(f"[{now}] {message}\n")


def pick_out_from_table(table_element, target):
    """
    HTMLのtable要素のthを検索してtdのテキストを返す
    一致するものがない場合はハイフン[-]を返す
    """
    # ここの繰り返しで処理が遅くなっていそう。
    # idやclass指定がないので、繰り返ししか方法がなさそう
    tr_elements = table_element.find_elements_by_tag_name("tr")
    for tr_element in tr_elements:
        th_element = tr_element.find_element_by_tag_name("th")
        if th_element.text == target:
            return tr_element.find_element_by_tag_name("td").text
    return '-'


def get_next_page_url(driver):
    """
    次のページのURLを返す
    ない場合は空文字を返す
    """
    next_page_elements = driver.find_elements_by_class_name("iconFont--arrowLeft")
    if next_page_elements:
        return next_page_elements[0].get_attribute("href")
    else:
        return ""


# main処理
def main():
    write_log_file("START PROGRAM")

    # 検索ワードが入力がされるまで繰り返す
    while True:
        search_keyword = input("検索ワードを入力してください：")
        if search_keyword:
            break

    # ドライバーの取得に失敗したら、処理を終了する
    try:
        driver = Chrome(ChromeDriverManager().install())
    except Exception as e:
        write_log_file(e)
        return None

    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)

    try:
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
        time.sleep(5)
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
    except:
        pass

    # 検索窓に入力
    driver.find_element_by_class_name(
        "topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

    # ページ終了まで繰り返し取得
    company_list = []

    # ログに使用するカウントを定義
    page_cnt = 0
    company_cnt = 0

    while True:
        # ページ内で要素の取得に失敗したら、次のページに進む
        # そのページすべてをスキップしていいのか？
        # elementsのリストで取得するので、１つだけ飛ばすことは難しそう
        try:
            page_cnt += 1
            write_log_file(f"Start Page {page_cnt}")

            # キャッチコピーを除いて会社名を取得
            name_list = [
                element.text.split()[0] for element in driver.find_elements_by_class_name("cassetteRecruit__name")]

            # 表から情報を取得
            table_elements = driver.find_elements_by_class_name("tableCondition")
            income_list = []
            description_list = []
            for table_element in table_elements:
                income_list.append(pick_out_from_table(table_element, "初年度年収"))
                description_list.append(pick_out_from_table(table_element, "仕事内容"))

            # 1ページ分繰り返し
            for name, income, description in zip(name_list, income_list, description_list):
                company_cnt += 1
                write_log_file(f"Start company {company_cnt}")
                company_list.append([name, income, description])

        except Exception as e:
            write_log_file(e)

        # 次のページに進む
        # ない場合は、ループを抜ける
        write_log_file(f"End Page {page_cnt}")
        next_page_url = get_next_page_url(driver)
        if next_page_url:
            driver.get(next_page_url)
            time.sleep(3)
        else:
            break

    # CSVファイルに結果を書き出す
    csv_header = ["会社名", "初年度年収", "仕事内容"]
    df_company = pd.DataFrame(company_list, columns=csv_header)

    csv_path = "result.csv"
    df_company.to_csv(csv_path, index=False)
    write_log_file(f"Write Resultfile {csv_path}")

    write_log_file("END PROGRAM")


# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
