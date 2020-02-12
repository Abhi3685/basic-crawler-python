import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

user_agent = 'Mozilla/5.0'
headers = {'User-Agent': user_agent }

# Connecting To MongoDB
client = MongoClient('mongodb+srv://root:almzsknx1029@cluster0-sri2t.mongodb.net/test?retryWrites=true&w=majority')
db = client.database 
booksCollection = db.books 
categoriesCollection = db.categories 

# Request to fetch list of categories
res = requests.get('https://manybooks.net/categories', headers=headers)
res = BeautifulSoup(res.text, 'html.parser')
for index, catCode in enumerate(res.select('a[href^="/categories/"]')):
	if index == 63:
		break
	catLink = "https://manybooks.net" + catCode['href']

	# Request to fetch list of books
	res2 = requests.get(catLink, headers=headers)
	res2 = BeautifulSoup(res2.text, 'html.parser')

	# Fetch category details
	catTitle = res2.select('.mb-title')[0].text
	if len(res2.select('.mb-description')):
		catDesc = res2.select('.mb-description')[0].text
	else:
		catDesc = "No description available for this category"
	category = {
		"title": catTitle,
		"description": catDesc
	}
	# Insert Category into DB
	categoriesCollection.update_one(category, {'$set': category}, upsert = True)
	print("Category #" + str(index + 1) + " Started")

	for i, link in enumerate(res2.select('.field.field--name-field-cover.field--type-image.field--label-hidden.field--item > a')):
		if i == 12:
			break
		# Request to fetch individual book details
		res3 = requests.get('https://manybooks.net' + link['href'], headers=headers)
		res3 = BeautifulSoup(res3.text, 'html.parser')
		# Filtering Book Details
		genres = []
		if len(res3.select('.field > img')):
			coverImg = "https://manybooks.net" + res3.select('.field > img')[0]['src']
		else:
			print("No Cover Image Found!")
			continue
		
		if len(res3.select('.mb-link-files')) > 0:
			if len(res3.select('.mb-link-files')[0]['href'].split('=')) > 1:
				bookId = res3.select('.mb-link-files')[0]['href'].split('=')[1]
				pdfUrl = "https://manybooks.net/books/get/" + bookId + "/6"
			else:
				print("No PDF Url Found!")
				continue
		else:
			print("No PDF Url Found!")
			continue

		if len(res3.select('.field')):
			title = res3.select('.field')[0].text
		else:
			print("No Title Found!")
			continue

		if len(res3.select('.field--items > .field--item')):
			author = res3.select('.field--items > .field--item')[0].text
		else:
			print("No Author Found!")
			continue

		if len(res3.select('.field--name-field-excerpt')):
			excerpt = res3.select('.field--name-field-excerpt')[0].text.replace("\n", "")
		else:
			excerpt = "No excerpt available for this book"
		for genre in res3.select('.field--name-field-genre > .field--item'):
			genres.append(genre.text)
		book = {
			"title": title,
			"author": author,
			"category": catTitle,
			"coverImg": coverImg,
			"pdfUrl": pdfUrl,
			"excerpt": excerpt,
			"genres": genres
		}
		# Insert Book into DB
		booksCollection.update_one(book, {'$set': book}, upsert = True)

		print("Book Inserted #" + str(i + 1))

	print("Category #" + str(index + 1) + " Ended")

print('Completed!')