import os
import sys
import json
import time
import openai
import pickle
import argparse
import requests
from tqdm import tqdm
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaForCausalLM, LlamaTokenizer

from fastchat.model import load_model, get_conversation_template, add_model_args


openai.api_key = "OPENAI_API_KEY"


# determinant vs. determiner
# https://wikidiff.com/determiner/determinant
ents_prompt = [
    'Noun',
    'Verb',
    'Adjective',
    'Adverb',
    'Preposition/Subord',
    'Coordinating Conjunction',
    # 'Cardinal Number',
    'Determiner',
    'Noun Phrase',
    'Verb Phrase',
    'Adjective Phrase',
    'Adverb Phrase',
    'Preposition Phrase',
    'Conjunction Phrase',
    'Coordinate Phrase',
    'Quantitave Phrase',
    'Complex Nominal',
    'Clause',
    'Dependent Clause',
    'Fragment Clause',
    'T-unit',
    'Complex T-unit',
    # 'Fragment T-unit',
]
ents = ['NN', 'VB', 'JJ', 'RB', 'IN', 'CC', 'DT', 'NP', 'VP', 'ADJP', 'ADVP', 'PP', 'CONJP', 'CP', 'QP', 'CN', 'C', 'DC', 'FC', 'T', 'CT']


model_mapping = {
    # 'gpt3': 'gpt-3',
    'gpt3.5': 'gpt-3.5-turbo-0613',
    'vicuna-7b': 'lmsys/vicuna-7b-v1.3',
    'vicuna-13b': 'lmsys/vicuna-13b-v1.3',
    'vicuna-33b': 'lmsys/vicuna-33b-v1.3',
    'fastchat-t5': 'lmsys/fastchat-t5-3b-v1.0',
    # 'llama2': 'meta-llama/Llama-2-7b-chat-hf',
    'llama-7b': '/data/jiali/llama/hf/7B',
    'llama-13b': '/data/jiali/llama/hf/13B',
    'llama-30b': '/data/jiali/llama/hf/30B',
    'llama-65b': '/data/jiali/llama/hf/65B',
    'alpaca': '/data/jiali/alpaca-7B',
    # 'koala-7b': 'koala-7b',
    # 'koala-13b': 'koala-13b',
}

for m in model_mapping.keys():
    for eid, ent in enumerate(ents):
        os.makedirs(f'result/openai_result/{m}/ptb/per_ent/{ent}', exist_ok=True)
        os.makedirs(f'result/structured_prompt/{m}/ptb', exist_ok=True)


# s = int(sys.argv[1])
# e = int(sys.argv[2])

s = 0
e = 1000
with open('ptb_corpus/sample_uniform_1k_2.txt', 'r') as f:
    selected_idx = f.readlines()
selected_idx = [int(i.strip()) for i in selected_idx][s:e]


ptb = []
with open('./ptb_corpus/ptb.jsonl', 'r') as f:
    for l in f:
        ptb.append(json.loads(l))


## Prompt 1
template_all = '''Please output the <Noun, Verb, Adjective, Adverb, Preposition/Subord, Coordinating Conjunction, Cardinal Number, Determiner, Noun Phrase, Verb Phrase, Adjective Phrase, Adverb Phrase, Preposition Phrase, Conjunction Phrase, Coordinate Phrase, Quantitave Phrase, Complex Nominal, Clause, Dependent Clause, Fragment Clause, T-unit, Complex T-unit, Fragment T-unit> in the following sentence without any additional text in json format: "{}"'''
template_single = '''Please output any <{}> in the following sentence one per line without any additional text: "{}"'''

## Prompt 2
with open('ptb_corpus/structured_prompting_demonstration_42.txt', 'r') as f:
    demonstration = f.read()


def para(m):
    c = 0
    for n, p in m.named_parameters():
        c += p.numel()
    return c

def main(args=None):

    if 'gpt3' in args.model:
        pass

    else:
        path = model_mapping[args.model]
        model, tokenizer = load_model(
            path,
            args.device,
            args.num_gpus,
            args.max_gpu_memory,
            args.load_8bit,
            args.cpu_offloading,
            revision=args.revision,
            debug=args.debug,
        )

    if args.prompt == 1:
        for gid in tqdm(selected_idx, desc='Query'):
            text = ptb[gid]['text']

            for eid, ent in enumerate(ents):
                # if os.path.exists(f'result/openai_result/{args.model}/ptb/per_ent/{ent}/{gid}.pkl') or \
                # os.path.exists(f'result/openai_result/{args.model}/ptb/per_ent/{ent}/{gid}.txt'):
                #     print(gid, ent, 'skip')
                #     continue

                ## Get prompt
                msg = template_single.format(ents_prompt[eid], text)

                if 'gpt' in args.model:
                    prompt = msg  

                elif 'vicuna' in args.model or 'alpaca' in args.model or 'fastchat-t5' in args.model:
                    conv = get_conversation_template(args.model)
                    conv.append_message(conv.roles[0], msg)
                    conv.append_message(conv.roles[1], None)
                    conv.system = ''
                    prompt = conv.get_prompt().strip()

                elif 'llama-' in args.model:
                    prompt = '### Human: ' + msg + ' ### Assistant:'


                ## Run
                if 'gpt3' in args.model:
                    outputs = gpt3(prompt)
                    
                else:
                    outputs = fastchat(prompt, model, tokenizer)

                with open(f'result/openai_result/{args.model}/ptb/per_ent/{ent}/{gid}.txt', 'w') as f:
                    f.write(outputs)


    if args.prompt == 2:
        for gid in tqdm(selected_idx, desc='Query'):
            text = ptb[gid]['text']

            if os.path.exists(f'result/structured_prompt/{args.model}/ptb/{gid}.pkl') or \
            os.path.exists(f'result/structured_prompt/{args.model}/ptb/{gid}.txt'):
                print(gid, 'skip')
                continue

            prompt = demonstration + '\n' + text

            if 'gpt3' in args.model:
                outputs = gpt3(prompt)

            else:
                outputs = fastchat(prompt, model, tokenizer)

            with open(f'result/structured_prompt/{args.model}/ptb/{gid}.txt', 'w') as f:
                f.write(outputs)


def fastchat(prompt, model, tokenizer):
    input_ids = tokenizer([prompt]).input_ids
    output_ids = model.generate(
        torch.as_tensor(input_ids).cuda(),
        do_sample=True,
        temperature=args.temperature,
        repetition_penalty=args.repetition_penalty,
        max_new_tokens=args.max_new_tokens,
    )

    if model.config.is_encoder_decoder:
        output_ids = output_ids[0]
    else:
        output_ids = output_ids[0][len(input_ids[0]) :]
    outputs = tokenizer.decode(
        output_ids, skip_special_tokens=True, spaces_between_special_tokens=False
    )

    # print('Empty system message')
    # print(f"{conv.roles[0]}: {msg}")
    # print(f"{conv.roles[1]}: {outputs}")

    return outputs


def gpt3(prompt):
    try:
        response = openai.ChatCompletion.create(
            model=args.model, messages=[{"role": "user", "content": prompt}])

        return response

    except Exception as err:
        print('Error')
        print(err)

    # time.sleep(1)
    raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_model_args(parser)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--repetition_penalty", type=float, default=1.0)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--message", type=str, default="Hello! Who are you?")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=1)
    parser.add_argument("--model", required=True, type=str, default=None)
    parser.add_argument("--prompt", required=True, type=int, default=None)
    args = parser.parse_args()

    # Reset default repetition penalty for T5 models.
    if "t5" in args.model and args.repetition_penalty == 1.0:
        args.repetition_penalty = 1.2

    main(args)
