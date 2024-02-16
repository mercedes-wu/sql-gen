import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class LLM:
    def __init__(self, model_name):
        self.model_name = model_name
        self.cuda_availability = torch.cuda.is_available()
        self.available_memory = torch.cuda.get_device_properties(0).total_memory
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def load_model(self):
        if self.available_memory > 15e9:
            # if you have atleast 15GB of GPU memory, run load the model in float16
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto",
                use_cache=True,
            )
        else:
            # else, load in 8 bits – this is a bit slower
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                # torch_dtype=torch.float16,
                load_in_8bit=True,
                device_map="auto",
                use_cache=True,
            )
        return model
    
    def generate_sql(self, prompt):
        model = self.load_model()
        eos_token_id = self.tokenizer.eos_token_id
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        generated_ids = model.generate(
            **inputs,
            num_return_sequences=1,
            eos_token_id=eos_token_id,
            pad_token_id=eos_token_id,
            max_new_tokens=400,
            do_sample=False,
            num_beams=1,
        )
        outputs = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        return outputs
    
    def empty_cuda_cache(self):
        # empty cache so that you do generate more results w/o memory crashing
        # particularly important on Colab – memory management is much more straightforward
        # when running on an inference service
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

class Prompt:
    def __init__(self, question, schema, table_description):
        self.question = question
        self.schema = schema
        self.table_description = table_description
    
    def create_prompt(self):
        prompt = f"""### Task
            Generate a SQL query to answer the following question:
            `{self.question}`

            ### Database Schema
            This query will run on a database whose schema is represented in this string:
            {self.schema}

            ### Database Description
            The description of the schema is represented in this string:
            {self.table_description}

            ### SQL
            Given the database schema, here is the SQL query that answers `{self.question}`:
            ```sql
        """
        return prompt
