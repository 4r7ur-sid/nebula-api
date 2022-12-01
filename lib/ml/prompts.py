import random
from lib.clients.open_ai import OpenAi
oi = OpenAi()


def generate_title(titles):
    titles = random.sample(titles, 3)
    prompt = "Generate an article title from the following titles:\n"
    for title in titles:
        prompt += f"{title}\n"
    prompt += "\n#\nTitle:"
    return oi.generate(prompt)


def generate_description(descriptions):
    descriptions = random.sample(descriptions, 3)
    prompt = "Generate an article description from the following descriptions:\n"
    for description in descriptions:
        prompt += f"{description}\n"
    prompt += "\n#\nDescription:"
    return oi.generate(prompt)


def generate_outline(outlines, meta):
    prompt = "Generate a comprehensive article Outline using the following outline Examples:\n\n"
    for (index, outline) in enumerate(outlines):
        prompt += f"# Example {index+1}\n"
        prompt += f"h1-{meta['competitors'][index]['text']}\n"
        for heading in outline["outline"]:
            if heading["tag"] not in ["h2", "h3"]:
                continue
            prompt += f"{heading['tag']}-{heading['text']}\n"
        prompt += "\n"
    if (len(prompt.split("\n"))) > 100:
        prompt = prompt.split("\n")[:100]
        prompt = "\n".join(prompt)
    if len(meta["ai"]) > 0:
        title = random.choice(meta["ai"])
    else:
        title = random.choice(meta["competitors"])["text"]
    prompt += f"\n\n\"\"\"\n#Outline:\nh1-{title}\nh2-"
    response = oi.generate(prompt)
    response = response.split("\n")
    output = []
    for heading in response:
        if heading.startswith("h2-"):
            output.append({"tag": "h2", "text": heading[3:]})
        elif heading.startswith("h3-"):
            output.append({"tag": "h3", "text": heading[3:]})
    return output
