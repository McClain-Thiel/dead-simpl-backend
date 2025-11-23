# Dead Simpl Backend

Simplified FastAPI backend with PostgreSQL.

# What is it?

Dead Simpl is a no code web app for evaluating, fine tuning and deploying large language models (LLMs)  for specific goals. 

- **Evaluation** is testing a model against specific use cases. You want to see how good a model is at X so you write a bunch of tests for it. You can think of it very similarly to how you might evaluate (test) a student.

| Question | Expected Answer | Models Answer |
| --- | --- | --- |
| A customer asks: "What's your return policy?" | <A clear explanation of the 30-day return policy with free shipping> | <A generic description of some random return policy > |
| Write a product description for a coffee maker | <A friendly, conversational description highlighting key features of *our* coffee maker> | <Description of a coffee maker> |
- **Fine tuning** is teaching a model to be better at your specific task. Think of it like training a general doctor to become a specialist. The model already knows language, but you're teaching it to respond in exactly the way you need for your particular use case.
- **Deployment** is making your model available for actual use. Once you've tested and trained your model, deployment means setting it up so your team or customers can actually use it in the real world, like launching a new tool or feature.

These 3 actions create a loop you can use to improve how good your model is out in the real world:

![Screenshot 2025-10-31 at 9.00.52 AM.png](attachment:1d7ef2d3-9a5c-4906-a841-d2e81a6970e7:Screenshot_2025-10-31_at_9.00.52_AM.png)

### Why is fine tuning necessary?

Off-the-shelf models are powerful, but they're built for everyone. Fine tuning lets you customize them for your specific needs:

- **Match your brand voice**: A generic model might sound formal and robotic. Fine tuning can teach it to sound friendly and casual like your startup, or professional and authoritative like your law firm.
- **Add industry-specific knowledge**: A general model doesn't know your company's products, your medical practice's procedures, or your restaurant's menu. Fine tuning gives it this specialized knowledge so it can answer questions accurately.
- **Fix unwanted behaviors**: Maybe the model keeps apologizing too much, or gives overly long answers, or uses jargon your customers don't understand. Fine tuning helps you correct these specific issues.
- **Follow your guidelines**: You might need responses in a specific format, want the model to always mention certain legal disclaimers, or require it to escalate certain types of questions to humans. Fine tuning teaches these rules.

<aside>
💡

**What about RAG?**

RAG (Retrieval-Augmented Generation) is like giving your model a library card. Instead of fine tuning the model itself, you give it access to your documents and let it look up relevant information when answering questions. It's faster and cheaper than fine tuning, but works best when you just need the model to reference specific information rather than change how it behaves or talks.

</aside>

Theres about 1000 papers that show that a smaller fine tuned model is as good or better than larger frontier models (GPT-5, Claude 4.5, ect) at specific tasks in addition to being faster, cheaper and owned by your org. 

# Why Dead Simpl?

### The Market Gap

When you google "fine tune llm" this is what comes up. There are all guides and "How Tos" not one single service provider, much less a no code option.

![Fine tuning is pretty easy at this point. Theres a reasonable number of knobs to turn but most AI engineers could do it with a bit of time. The difficult part is the data and ops. ](attachment:e3521673-8f41-4eca-87e6-8b7bc3f0b554:Screenshot_2025-10-31_at_9.06.55_AM.png)

Fine tuning is pretty easy at this point. There are a reasonable number of knobs to turn but most AI engineers could do it with a bit of time. **The difficult part is the data and ops.**

But here's the problem: **AI engineers are rare and expensive.** Most companies don't have them, and the ones that do can't keep up with demand. Meanwhile, these same companies are full of project managers, operations specialists, and data analysts who already know their business inside and out.

### Who This Is For

Dead Simpl is built for the people companies already have:

- **Project managers** who understand what the business needs but can't code the solution
- **Operations specialists** who know where the problems are but need technical help to fix them
- **Business teams** who want to experiment with AI without waiting for engineering resources

These people don't need to understand neural networks or transformers. They need to understand their business, their customers, and their data. And that's exactly what they're already good at.

### Why This Works

Writing evaluations doesn't require a computer science degree. If you can write "What should our chatbot say when a customer asks about returns?" you can write an evaluation. If you can create example responses in a spreadsheet, you can create training data.

The technical complexity of fine tuning, deployment, and infrastructure shouldn't require an AI engineer. Organizations are already excellent at managing people who work with data and processes. Dead Simpl lets them apply that existing strength to LLM development.

Instead of hiring scarce AI engineering talent, companies can empower the people they already have to build and improve their AI systems. The AI engineers who do exist can focus on truly complex problems instead of repetitive fine tuning tasks.

## Local Development

### Prerequisites
- Docker
- Docker Compose

### Running Locally

```bash
# Start the backend and database
docker-compose up

# The API will be available at http://localhost:8000
# Health check: http://localhost:8000/health
```

### Stopping

```bash
docker-compose down
```

### Database

The database schema is automatically created on startup using SQL migrations in `migrations/init.sql`.

Currently includes:
- Users table with ranks (admin, user, expired, waitlist)

## CI/CD

Simple GitHub Actions workflow runs on push to main/staging:
- Builds and starts services via docker-compose
- Checks health endpoint
- Stops services

## Project Structure

```
├── app/
│   ├── db/               # Database models and connection
│   ├── routers/          # API route handlers
│   ├── schemas/          # Pydantic schemas
│   ├── middleware/       # Custom middleware
│   └── main.py           # FastAPI app
├── migrations/
│   └── init.sql          # Initial database schema
├── docker-compose.yml    # Local development setup
├── Dockerfile            # Backend container
└── .github/workflows/    # CI configuration
```
