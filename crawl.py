from icrawler.builtin import BaiduImageCrawler, BingImageCrawler, GoogleImageCrawler

RAW_FOLDER = "Dataset/data_raw_new/"
KEY_WORD_FILE = "idol2.txt"


def Crawl_Image(key_word, raw_folder=RAW_FOLDER):
    google_crawler = GoogleImageCrawler(
        feeder_threads=1,
        parser_threads=1,
        downloader_threads=6,
        storage={'root_dir': raw_folder + key_word})

    google_crawler.crawl(keyword=key_word, offset=0, max_num=1000,
                         min_size=None, max_size=None, file_idx_offset=0)
    bing_crawler = BingImageCrawler(downloader_threads=6, storage={'root_dir': raw_folder + key_word})
    bing_crawler.crawl(keyword=key_word, filters={'type': 'photo'}, offset=0, max_num=1000)

    baidu_crawler = BaiduImageCrawler(storage={'root_dir': raw_folder + key_word})
    baidu_crawler.crawl(keyword=key_word, offset=0, max_num=1000,
                        min_size=None, max_size=None)


# Open file key word
with open(KEY_WORD_FILE, mode="r") as file:
    key_word = file.read()
    key_word = key_word.split("\n")

# Crawl image
for kw in key_word[0:-1]:
    print("Start crawl image about ", kw)
    Crawl_Image(kw, RAW_FOLDER)
    print("Done! Crawled image about " + str(kw))

print("Done! Crawled " + str(len(key_word) - 1) + " idol")
