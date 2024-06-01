from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
print("Gokcenaz")


# Let's chat for 5 lines
for step in range(5):
    tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-large')
    model = AutoModelForCausalLM.from_pretrained('microsoft/DialoGPT-small')
    # encode the new user input, add the eos_token and return a tensor in Pytorch
    new_user_input_ids = tokenizer.encode(tokenizer.eos_token + input(">> User:"), return_tensors='pt')

    # append the new user input tokens to the chat history
    bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

    # generated a response while limiting the total chat history to 1000 tokens, 
    chat_history_ids = model.generate(
        bot_input_ids,
        max_length=1000, 
        pad_token_id=tokenizer.eos_token_id, 
        no_repeat_ngram_size=3,
        do_sample=True,
        top_k=100,
        top_p=0.7,
        temperature = 0.1,
                                      )
  
    # pretty print last ouput tokens from bot
    print("GokcenazBot: {}".format(tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0]).replace("<|endoftext|>", "")))