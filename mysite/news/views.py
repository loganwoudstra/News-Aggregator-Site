import requests
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
from news.models import Article, Preferences

news_companies = ['Global', 'CBC', 'BBC', 'Yahoo', 'Google', 'NPR', 'Time', 'Atlantic', 'VOX', 'ESPN', 'Forbes']


def user_preferences(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            list_of_companies = request.POST.getlist('companies')

            user_companies = Preferences.objects.get(user=request.user)
            for company in news_companies:
                if company in list_of_companies:
                    setattr(user_companies, company, True)
                else:
                    setattr(user_companies, company, False)
            user_companies.save()

        context = {
            'news_companies': news_companies,
            'user_data': Preferences.objects.get(user=request.user),
        }

        return render(request, "news/user_preferences.html", context)

    else:  # if user is not logged into ana account they are redirected to a login page
        return redirect("/login")



def home(request):
    Article.objects.all().delete()  # deletes all old articles and scrapes most current news

    def savearticle(headline, image, link, company):
        new_article = Article()
        new_article.headline = headline
        new_article.image = image
        new_article.link = link
        new_article.company = company
        new_article.save()

    def global_news(html_text):
        company = "Global"
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find('main', class_='l-main').find_all('li', class_='c-posts__item')[:7]

        for index, story in enumerate(articles):
            if index != 5:
                headline = story.find('span', class_='c-posts__headlineText').text
                image = story.find('div', class_='c-posts__media').img['data-src']
                link = story.a['href']
                savearticle(headline, image, link, company)

    def cbc_news(html_text):
        company = "CBC"
        soup = BeautifulSoup(html_text, 'lxml')

        # top story has a different tag and class
        top_story = soup.find('div', class_='card')
        top_story_headline = top_story.find('h3', class_='headline').text
        top_story_link = 'https://www.cbc.ca' + top_story.a['href']
        try:  # if top story image is an image
            top_story_image = top_story.find('div', class_='placeholder').img['src']
        except:  # if top story uses a video
            top_story_image = top_story.find('img', class_='thumbnail')['src']
        savearticle(top_story_headline, top_story_image, top_story_link, company)

        # other stories aside from top story
        articles = soup.find_all('a', class_='cardListing')[:6]
        for article in articles:
            headline = article.find('h3', class_='headline').text
            image = article.find('img')['src']
            link = 'https://www.cbc.ca' + article['href']
            savearticle(headline, image, link, company)

    def bbc_news(html_text):
        company = "BBC"
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find('div', class_='gel-layout gel-layout--equal').find_all('div', class_='gs-c-promo')[:6]

        for article in articles:
            headline = article.find('h3').text
            link = 'https://www.bbc.com' + article.find('a')['href']

            # for some reason some images are different from the inspected html and need to use 'data-src' while
            # manually inputting width, rather than just 'src'
            try:
                image = article.find('img')['data-src'].replace('{width}', '490')
            except:
                image = article.find('img')['src']
            savearticle(headline, image, link, company)

    def yahoo_news(html_text):
        company = "Yahoo"
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find_all('li', class_='js-stream-content')[:10]
        articles_with_images = 0  # not every article has an image, so it cycles through the first ten until it finds 6 with

        for article in articles:  # images
            try:
                image = article.find('img')['src']
                articles_with_images += 1
            except:
                continue
            headline = article.find('h3').a.text
            link = 'https://ca.news.yahoo.com' + str(article.find('h3').a['href'])
            savearticle(headline, image, link, company)
            if articles_with_images == 6:
                break

    def google_news(html_text):
        company = "Google"
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find_all('div', class_='NiLAwe')[:6]

        for article in articles:
            headline = article.find('h3').a.text
            image = article.find('img')['src']
            link = 'https://news.google.com' + str(article.find('a', class_='VDXfz')['href'])
            savearticle(headline, image, link, company)

    def npr_news(html_text):
        company = "NPR"
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find_all('article', class_='has-image')[:6]

        for article in articles:
            try:
                image = article.find('img')['src']
            except:  # if an article is a live stream
                continue
            headline = article.find('h3').text
            link = article.find('a')['href']
            savearticle(headline, image, link, company)

    def time_news(html_text):
        company = "Time"
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find_all('article')[:6]

        for article in articles:
            headline = article.find('h3').a.text.strip()
            image = article.find('img')['src']
            link = 'https://time.com/' + str(article.find('h3').a['href'])
            savearticle(headline, image, link, company)

    def atlantic_news(html_text):
        company = "Atlantic"
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find_all('article')[:6]

        for index, article in enumerate(articles):
            if index == 0:  # first story has diffrent class names as the other stories
                headline = article.find('h1', class_='o-hed').text.strip()
                image = article.find('img')['srcset'].split(',')[
                    0]  # given two links of same image so needs to be split
            else:
                headline = article.find('h2', class_='o-hed').text.strip()
                image = article.find('img')['data-srcset'].split(',')[0]
            link = article.find('a', class_='o-media__object')['href']
            savearticle(headline, image, link, company)

    def vox_news(html_text):
        company = "VOX"
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find_all('div',
                                 class_='c-entry-box-base')  # first two articles have different class than the rest
        articles.extend(soup.find_all('div', class_='c-compact-river__entry')[:4])

        for index, article in enumerate(articles):
            if index < 2:  # first 2 headlines are h3 and the rest are h2
                headline = article.find('h3').a.text
                image = str(article.find('script')).split()[-4].split('"')[1]  # images in 'img' can't be scraped unless
                # you have access to the API so you have to get it through this weird way
            else:
                headline = article.find('h2').a.text
                image = str(article.find('noscript')).split()[2].split('"')[1]
            link = article.find('a')['href']
            savearticle(headline, image, link, company)

    def espn_news(html_text):
        company = "ESPN"
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find_all('section', class_='contentItem__content')[:10]
        articles_found = 0  # some 'article' are videos with no link

        for article in articles:
            try:
                link = 'https://www.espn.com/' + str(article.find('a')['href'])
                articles_found += 1
            except:
                continue
            headline = article.find('h1').text
            image = article.find('img')['data-default-src']
            savearticle(headline, image, link, company)
            if articles_found == 6:
                break

    def forbes_news(html_text):
        company = "Forbes"
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find_all('div', class_='card')[:6]

        for article in articles:
            headline = article.find('a', class_='headlink').text
            image = article.find('progressive-image')['background-image']
            link = article.find('a', class_='headlink')['href']
            savearticle(headline, image, link, company)

    # link of news sites
    global_news_html_text = requests.get('https://globalnews.ca/edmonton/').text
    cbc_news_html_text = requests.get('https://www.cbc.ca/news').text
    bbc_news_html_text = requests.get('https://www.bbc.com/news/world').text
    yahoo_news_html_text = requests.get('https://ca.news.yahoo.com/world/').text
    google_news_html_text = requests.get('https://news.google.com/topics'
                                         '/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pEUVNnQVAB?hl=en-CA&gl=CA'
                                         '&ceid''=CA:en').text
    npr_news_html_text = requests.get('https://www.npr.org/').text
    time_news_html_text = requests.get('https://time.com/section/world/').text
    atlantic_news_html_text = requests.get('https://www.theatlantic.com/').text
    vox_news_html_text = requests.get('https://www.vox.com/world').text
    espn_news_html_text = requests.get('https://www.espn.com/').text
    forbes_news_html_text = requests.get('https://www.forbes.com/innovation/?sh=54a736c76834').text

    # shows user their preferred sites if they are logged in
    if request.user.is_authenticated:
        preferred_sites = 0
        company_list = []
        if Preferences.objects.get(user=request.user).Global:
            preferred_sites+=1
            company_list.append('Global')
            global_news(global_news_html_text)
        if Preferences.objects.get(user=request.user).CBC:
            preferred_sites += 1
            company_list.append('CBC')
            cbc_news(cbc_news_html_text)
        if Preferences.objects.get(user=request.user).BBC:
            preferred_sites += 1
            company_list.append('BBC')
            bbc_news(bbc_news_html_text)
        if Preferences.objects.get(user=request.user).Yahoo:
            preferred_sites += 1
            company_list.append('Yahoo')
            yahoo_news(yahoo_news_html_text)
        if Preferences.objects.get(user=request.user).Google:
            preferred_sites += 1
            company_list.append('Google')
            google_news(google_news_html_text)
        if Preferences.objects.get(user=request.user).NPR:
            preferred_sites += 1
            company_list.append('NPR')
            npr_news(npr_news_html_text)
        if Preferences.objects.get(user=request.user).Time:
            preferred_sites += 1
            company_list.append('Time')
            time_news(time_news_html_text)
        if Preferences.objects.get(user=request.user).Atlantic:
            preferred_sites += 1
            company_list.append('Atlantic')
            atlantic_news(atlantic_news_html_text)
        if Preferences.objects.get(user=request.user).VOX:
            preferred_sites += 1
            company_list.append('VOX')
            vox_news(vox_news_html_text)
        if Preferences.objects.get(user=request.user).ESPN:
            preferred_sites += 1
            company_list.append('ESPN')
            espn_news(espn_news_html_text)
        if Preferences.objects.get(user=request.user).Forbes:
            preferred_sites += 1
            company_list.append('Forbes')
            forbes_news(forbes_news_html_text)

        if preferred_sites == 0:  # redirects users to their preferences if no sites are selected
            context = {
                'news_companies': news_companies,
                'user_data': Preferences.objects.get(user=request.user),
            }
            return render(request, 'news/user_preferences.html', context)

    # shows user all news outlets if they are not logged in
    else:
        global_news(global_news_html_text)
        cbc_news(cbc_news_html_text)
        bbc_news(bbc_news_html_text)
        yahoo_news(yahoo_news_html_text)
        google_news(google_news_html_text)
        npr_news(npr_news_html_text)
        time_news(time_news_html_text)
        atlantic_news(atlantic_news_html_text)
        vox_news(vox_news_html_text)
        espn_news(espn_news_html_text)
        forbes_news(forbes_news_html_text)
        company_list = news_companies

    articles = Article.objects.all()[::-1]
    context = {
        'object_list': articles,
        'company_list': company_list,
    }
    return render(request, "news/home.html", context)
