import requests

# url = "https://images.pexels.com/photos/617278/pexels-photo-617278.jpeg"
# url = "https://fundusz.org/wp-content/uploads/2016/09/cropped-KFnrD_logoRGB.png"
url = "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=500&q=60"
res = requests.post('http://localhost:5000/api/v1/slides', json={"url": url})
if res.ok:
    print(res.content)
