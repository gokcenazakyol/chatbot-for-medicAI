from flask import Flask, render_template, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import requests
from bs4 import BeautifulSoup

tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-large')
model = AutoModelForCausalLM.from_pretrained('gokcenazakyol/medical-literature-small')

app = Flask(__name__)

@app.get("/")
def index_get():
    return render_template('base.html')

def web_scraping(qs):
    global flag2
    global loading

    URL = 'https://www.google.com/search?q=' + qs
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    links = soup.findAll("a")
    all_links = []
    for link in links:
        link_href = link.get('href')
        if "url?q=" in link_href and not "webcache" in link_href:
            all_links.append((link.get('href').split("?q=")[1].split("&sa=U")[0]))

    flag = False
    for link in all_links:
        if 'https://en.wikipedia.org/wiki/' in link:
            wiki = link
            flag = True
            break

    div0 = soup.find_all('div', class_="kvKEAb")
    div1 = soup.find_all("div", class_="Ap5OSd")
    div2 = soup.find_all("div", class_="nGphre")
    div3 = soup.find_all("div", class_="BNeawe iBp4i AP7Wnd")

    if len(div0) != 0:
        return div0[0].text
    elif len(div1) != 0:
        return div1[0].text + "\n" + div1[0].find_next_sibling("div").text
    elif len(div2) != 0:
        return div2[0].find_next("span").text + "\n" + div2[0].find_next("div", class_="kCrYT").text
    elif len(div3) != 0:
        return div3[1].text
    elif flag == True:
        page2 = requests.get(wiki)
        soup = BeautifulSoup(page2.text, 'html.parser')
        title = soup.select("#firstHeading")[0].text

        paragraphs = soup.select("p")
        for para in paragraphs:
            if bool(para.text.strip()):
                return title + "\n" + para.text
    return ""

@app.post("/predict")
def predict():
    input = request.get_json().get("message")
    response = web_scraping(input)
    if response != "":
        print(response)
        message = {"answer": response}
        return jsonify(message)
    for step in range(1):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(input + tokenizer.eos_token, return_tensors='pt')

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens,
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        response = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    message = {"answer": response}
    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)