# HR Assistant System

შპს „ნორთსტარ სერვისეზი"-ს ხელოვნური ინტელექტის მქონე HR ასისტენტი — Python CLI აპლიკაცია, რომელიც ქართულ ენაზე ელაპარაკება თანამშრომლებს, პასუხობს HR პოლიტიკის კითხვებს, აჩვენებს შვებულების ბალანსს და ქმნის შვებულების მოთხოვნებს.

---

## სისტემის მოთხოვნები

- Python 3.10 ან უფრო ახალი
- pip
- ინტერნეტ კავშირი (API-სა და Gemini-სთვის)

---

## სწრაფი გაშვება

### ნაბიჯი 1 — პროექტის ჩამოტვირთვა

```bash
git clone <your-repo-url>
cd "northstar system"
```

### ნაბიჯი 2 — ვირტუალური გარემოს შექმნა

```bash
python -m venv venv
```

გააქტიურება **Windows**-ზე:
```powershell
.\venv\Scripts\activate
```

გააქტიურება **macOS/Linux**-ზე:
```bash
source venv/bin/activate
```

### ნაბიჯი 3 — დამოკიდებულებების დაყენება

```bash
pip install -r hr_assistant_project/requirements.txt
```

> **შენიშვნა:** `docx2txt` პაკეტი საჭიროა `.docx` ფაილების ჩასატვირთად. თუ ინსტალაცია ვერ ხერხდება ავტომატურად:
> ```bash
> pip install docx2txt
> ```

### ნაბიჯი 4 — გარემოს ცვლადების კონფიგურაცია

დააკოპირეთ `.env.example` ფაილი:

```bash
cp hr_assistant_project/.env.example hr_assistant_project/.env
```

შეასწორეთ `.env` ფაილი:

```env
# Backend API URL — წინასწარ გაჰოსტილი
API_BASE_URL=https://bdoproject-back.onrender.com

# Google Gemini API გასაღები
# მიიღეთ უფასოდ: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=თქვენი_გასაღები_აქ
```

> **Backend API:** `https://bdoproject-back.onrender.com` — ეს არ სერვისი ASP.NET Core-ზე, რომელიც მართავს HR მონაცემების ბაზას (PostgreSQL). API დოკუმენტაცია: [`https://bdoproject-back.onrender.com/swagger`](https://bdoproject-back.onrender.com/swagger) ასევე: https://bdoproject-back.onrender.com/graphql

### ნაბიჯი 5 — HR დოკუმენტების ინდექსირება (RAG)

ეს ნაბიჯი მხოლოდ ერთხელ არის საჭირო (ან დოკუმენტების შეცვლისას):

```bash
python hr_assistant_project/rag/ingest.py
```

ეს სკრიპტი წაიკითხავს `documents/` საქაღალდეს, დაამუშავებს 7 HR დოკუმენტს და შეინახავს ვექტორულ ბაზას `hr_assistant_project/chroma_db/`-ში.

მოსალოდნელი გამოტანა:
```
Loading documents from .../documents...
Loaded 27 document fragments.
Created 115 chunks.
Generating embeddings...
Saving to ChromaDB...
Ingestion complete!
```

### ნაბიჯი 6 — აპლიკაციის გაშვება

```bash
python hr_assistant_project/cli/main.py
```

გაიხსნება ინტერაქტიული CLI:
```
HR Assistant System CLI
შეიყვანეთ ელ-ფოსტა: tamar.jorjadze@northstar.example
შეიყვანეთ Employee ID: E1007
მიმდინარეობს ავთენტიფიკაცია...
ავტორიზაცია წარმატებულია.
...
HR ასისტენტი მზად არის. (გამოსასვლელად აკრიფეთ 'exit')

თანამშრომელი: გამარჯობა
HR ასისტენტი:
შპს „ნორთსტარ სერვისეზი"-ს HR ასისტენტი მოგესალმებით. ...
```

---

## საჭირო API გასაღებები

| სერვისი | სად მიიღოთ | გასაღების სახელი `.env`-ში |
|---|---|---|
| Google Gemini | [aistudio.google.com](https://aistudio.google.com/app/apikey) | `GEMINI_API_KEY` |

Backend API გასაღები **არ საჭიროება** — ავთენტიფიკაცია ხდება ელ-ფოსტა/Employee ID წყვილით.
