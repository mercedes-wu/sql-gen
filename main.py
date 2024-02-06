import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import sqlparse


def initialize_model_and_tokenizer(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        # torch_dtype=torch.float16,
        # load_in_8bit=True,
        load_in_4bit=True,
        device_map="auto",
        use_cache=True,
    )

    return model, tokenizer


def create_prompt(question, schema):
    prompt = f"""### Task
        Generate a SQL query to answer the following question:
        `{question}`

        ### Database Schema
        This query will run on a database whose schema is represented in this string:
        {schema}

        ### SQL
        Given the database schema, here is the SQL query that answers `{question}`:
        ```sql
    """

    return prompt


def generate_sql(model, tokenizer, prompt):
    eos_token_id = tokenizer.eos_token_id
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    generated_ids = model.generate(
        **inputs,
        num_return_sequences=1,
        eos_token_id=eos_token_id,
        pad_token_id=eos_token_id,
        max_new_tokens=400,
        do_sample=False,
        num_beams=1,
    )
    outputs = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

    return outputs

def empty_cuda_cache():
    # empty cache so that you do generate more results w/o memory crashing
    # particularly important on Colab – memory management is much more straightforward
    # when running on an inference service
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

def main(): 
    print(f'CUDA availability: {torch.cuda.is_available()}')

    model_name = "codellama/CodeLlama-34b-hf"
    question = "What is our total revenue by product in the last week?"
    schema = """
        CREATE TABLE products (
        product_id INTEGER PRIMARY KEY, -- Unique ID for each product
        name VARCHAR(50), -- Name of the product
        price DECIMAL(10,2), -- Price of each unit of the product
        quantity INTEGER  -- Current quantity in stock
        );

        CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY, -- Unique ID for each customer
        name VARCHAR(50), -- Name of the customer
        address VARCHAR(100) -- Mailing address of the customer
        );

        CREATE TABLE salespeople (
        salesperson_id INTEGER PRIMARY KEY, -- Unique ID for each salesperson
        name VARCHAR(50), -- Name of the salesperson
        region VARCHAR(50) -- Geographic sales region
        );

        CREATE TABLE sales (
        sale_id INTEGER PRIMARY KEY, -- Unique ID for each sale
        product_id INTEGER, -- ID of product sold
        customer_id INTEGER,  -- ID of customer who made purchase
        salesperson_id INTEGER, -- ID of salesperson who made the sale
        sale_date DATE, -- Date the sale occurred
        quantity INTEGER -- Quantity of product sold
        );

        CREATE TABLE product_suppliers (
        supplier_id INTEGER PRIMARY KEY, -- Unique ID for each supplier
        product_id INTEGER, -- Product ID supplied
        supply_price DECIMAL(10,2) -- Unit price charged by supplier
        );

        -- sales.product_id can be joined with products.product_id
        -- sales.customer_id can be joined with customers.customer_id
        -- sales.salesperson_id can be joined with salespeople.salesperson_id
        -- product_suppliers.product_id can be joined with products.product_id
    """
    
    model, tokenizer = initialize_model_and_tokenizer(model_name)
    prompt = create_prompt(question, schema)

    sql_output = generate_sql(model, tokenizer, prompt)
    formatted_sql = sqlparse.format(sql_output[0].split("```sql")[-1], reindent=True)
    print(formatted_sql)

    return formatted_sql


if __name__ == '__main__':

    main()