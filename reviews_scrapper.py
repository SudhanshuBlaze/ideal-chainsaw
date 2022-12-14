from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from fastapi import FastAPI, Response
from sentiment_analysis import sentiment_analysis
from keyword_extraction import keyword_extraction
from word_cloud import wordcloud
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
import uvicorn



app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def reviews():
    options = webdriver.ChromeOptions()
    # options= Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('-headless')
    options.add_argument('-no-sandbox')
    options.add_argument('-disable-dev-shm-usage')


    # url="https://www.google.com/maps/place/Happy+Home+School/@22.2618037,84.8870326,19.26z/data=!4m7!3m6!1s0x3a201d9167666c77:0x7a65f976c2b26d33!8m2!3d22.2622776!4d84.8867239!9m1!1b1"
    url="https://www.google.com/maps/place/State+Bank+Of+India/@22.2558208,84.8882918,16.67z/data=!4m7!3m6!1s0x3a201c2a222c256b:0xd43e5ebc8e9da67b!8m2!3d22.2552897!4d84.8935059!9m1!1b1"

    # url="https://www.google.com/maps/place/CWS+Hospital/@22.2558208,84.8882918,16z/data=!4m14!1m6!3m5!1s0x3a201c2a222c256b:0xd43e5ebc8e9da67b!2sState+Bank+Of+India!8m2!3d22.2552897!4d84.8935059!3m6!1s0x3a201c2ca6e5da79:0xd1e929836dc72b94!8m2!3d22.255401!4d84.9008933!9m1!1b1"

    

    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    # browser = webdriver.Chrome('./chromedriver',options=options)

    browser.get(url)
    # print(browser.page_source)  # results

    num_of_reviews=browser.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]').text.split(" ")[0]
   

    #Find scroll layout
    scrollable_div = browser.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')

    #Scroll as many times as necessary to load all reviews
    num_of_scroll=round(int(num_of_reviews)/10 - 1)
    for i in range(num_of_scroll):
        browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', 
                scrollable_div)
        time.sleep(2)

    review_span = browser.find_elements(by=By.CLASS_NAME,value="wiI7pd")
    rating_span = browser.find_elements(by=By.CLASS_NAME,value="kvMYJc")
    
    #code for aggregating reviews and ratings
    reviews_arr=[]
    ratings_arr=[]
    for i in range(len(review_span)):
          if len(review_span[i].text)!=0:
                  #putting reviews in reviews_arr
                  reviews_arr.append(review_span[i].text)
                  #putting ratings in ratings_arr
                  ratings=rating_span[i].get_attribute("aria-label").split(" ")[1]
                  if int(ratings)>3:
                          ratings_arr.append("Positive")
                  else:
                          ratings_arr.append("Negative")

#--------------------------------------------------------------------------------------------------#
    #code for classifying reviews into positive or negative
    positive=[]
    negative=[]
    
    for i in range(len(ratings_arr)):
        if ratings_arr[i]=="Positive":
            positive.append(reviews_arr[i])
        else:
            negative.append(reviews_arr[i])

    sentiment_dict = {"Positive" : positive,"Negative" : negative }
    
    #keyword extraction
    keywords_dict = keyword_extraction(sentiment_dict)

    # word_cloud = wordcloud(keywords_dict)


    # img = BytesIO()
    # print(type(img))
    # word_cloud.to_image().save(img, 'PNG')
    # img.seek(0)
    # return Response(content=img, media_type="image/png")
    return keywords_dict

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
