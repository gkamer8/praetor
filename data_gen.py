import openai
from secrets import OPENAI_API_KEY, OPENAI_ORG_ID
import json
import os

PROMPT_FILES = {
    'coding': {
        'outfile': 'coding_prompts.json',
        'gen_qs_prompt': 'gen_coding_qs_prompt.txt',
        'example_qs': 'example_coding_prompts.txt'
    },
    'philosophy': {
        'outfile': 'phil_prompts.json',
        'gen_qs_prompt': 'gen_phil_qs_prompt.txt',
        'example_qs': 'example_phil_prompts.txt'
    },
    'politics': {
        'outfile': 'prompts.json',
        'gen_qs_prompt': 'gen_qs_prompt.txt',
        'example_qs': 'example_prompts.txt'
    }
}

ROOT_DIR = "data_gen_prompts"

def get_gpt_answer_prompt(instruction, prompt_file="prompt.txt"):

    with open(prompt_file, "r") as fhand:
        structure = fhand.read()
    return structure.format(instruction=instruction)

def get_gpt_answer(instruction):
    prompt = get_gpt_answer_prompt(instruction)
    openai.organization = OPENAI_ORG_ID
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=512,
        temperature=0.7,
        presence_penalty=1,
        frequency_penalty=1
    )

    # the zero implies k = 1
    completion = response['choices'][0]['text']
    return completion


def get_more_prompts(prompt_file, example_file):
    with open(example_file, "r") as fhand:
        examples = fhand.read().rstrip().split("\n")
    with open(prompt_file, "r") as fhand:
        prompt = fhand.read().rstrip()

    listed = "\n".join([f"{i+1}. {examples[i]}" for i in range(len(examples))])
    prompt = f"{prompt}:\n\n{listed}"
    

    openai.organization = OPENAI_ORG_ID
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=2048,
        temperature=0.7,
        presence_penalty=.5,
        frequency_penalty=0,
        best_of=2
    )

    # the zero implies k = 1
    completion = response['choices'][0]['text']
    lines = completion.split("\n")
    qs = examples + [x[x.index(".") + 2:] for x in lines if "." in x]
    return qs


# Takes a subject, which is a subdir of root_dir (e.g, 'politics'), and uses associated files
#   in PROMPT_FILES to generate new questions for answering
def gen_prompts(subject, root_dir=ROOT_DIR, quiet=False):
    prompts_dir = os.path.join(root_dir, subject)

    outfile = os.path.join(prompts_dir, PROMPT_FILES[subject]['outfile'])
    gen_qs_prompt_path = os.path.join(prompts_dir, PROMPT_FILES[subject]['gen_qs_prompt'])
    example_qs_path = os.path.join(prompts_dir, PROMPT_FILES[subject]['example_qs'])

    qs = get_more_prompts(gen_qs_prompt_path, example_qs_path)
    if not quiet:
        print(qs)
    json.dump(qs, open(outfile, "w"))


# file_paths should be a list of filepaths with prompts
def get_responses(file_paths, outfile_paths, quiet=False):
    if not quiet:
        print(f"Outputting to: {outfile_paths}")
    for path, outpath in zip(file_paths, outfile_paths):
        prompts = json.load(open(path, "r"))
        completions = []
        for i, prompt in enumerate(prompts):
            print(f"#{i} in {path}")
            if not quiet:
                print(f"Prompt: {prompt}")
            completion = get_gpt_answer(prompt)
            if not quiet:
                print(f"Completion: {completion}")
            completions.append(completion)
            
        structured_data = [{
                                'instruction': prompts[i],
                                'completion': completions[i]
                            } for i in range(len(completions))]
        json.dump(structured_data, open(outpath, "w"))


if __name__ == '__main__':
    # subject = 'politics'
    # gen_prompts(subject)
    paths = [os.path.join(ROOT_DIR, x, PROMPT_FILES[x]['outfile']) for x in PROMPT_FILES]
    outfile_paths = [os.path.join(ROOT_DIR, x, "structured_finetuning_data.json") for x in PROMPT_FILES]
    get_responses(paths, outfile_paths)
    