import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import sqlparse


def initialize_model_and_tokenizer(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    available_memory = torch.cuda.get_device_properties(0).total_memory
    if available_memory > 15e9:
        # if you have atleast 15GB of GPU memory, run load the model in float16
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto",
            use_cache=True,
        )
    else:
        # else, load in 8 bits – this is a bit slower
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            # torch_dtype=torch.float16,
            load_in_8bit=True,
            device_map="auto",
            use_cache=True,
        )

    return model, tokenizer


def create_prompt(question, schema, description):
    prompt = f"""### Task
        Generate a SQL query to answer the following question:
        `{question}`

        ### Database Schema
        This query will run on a database whose schema is represented in this string:
        {schema}

        ### Database Description
        The description of the schema is represented in this string:
        {description}

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

    model_name = "defog/sqlcoder-7b-2"
    question = """
        Return all the orders for Michael P.? Use the analytics schema for all tables in the query
        Use the postgres sql syntax.
        Adhere to these rules:
        - **Deliberately go through the question and database schema word by word** to appropriately answer the question
        - **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
        - When creating a ratio, always cast the numerator as float
    """
    schema = """
        CREATE TABLE analytics.customers (
            first_order date,
            number_of_orders bigint,
            customer_lifetime_value bigint,
            customer_id integer,
            most_recent_order date,
            first_name text,
            last_name text
        );

        CREATE TABLE analytics.orders (
            amount bigint,
            customer_id integer,
            order_date date,
            order_id integer,
            credit_card_amount bigint,
            coupon_amount bigint,
            bank_transfer_amount bigint,
            gift_card_amount bigint,
            status text
        );

        -- customers.customer_id can be joined with orders.customer_id
    """
    table_description = """
        name: customers
        description: This table has basic information about a customer, as well as some derived facts based on a customer's orders
        columns:
        - name: customer_id
            description: This is a unique identifier for a customer
            tests:
            - unique
            - not_null
        - name: first_name
            description: Customer's first name. PII.
        - name: last_name
            description: Customer's last name. PII.
        - name: first_order
            description: Date (UTC) of a customer's first order
        - name: most_recent_order
            description: Date (UTC) of a customer's most recent order
        - name: number_of_orders
            description: Count of the number of orders a customer has placed
        - name: total_order_amount
            description: Total value (AUD) of a customer's orders
    """
    
    model, tokenizer = initialize_model_and_tokenizer(model_name)
    prompt = create_prompt(question, schema, table_description)

    sql_output = generate_sql(model, tokenizer, prompt)

    formatted_sql = sqlparse.format(sql_output[0].split("```sql")[-1], reindent=True)
    print(formatted_sql)

    empty_cuda_cache()

    return formatted_sql


if __name__ == '__main__':
    main()