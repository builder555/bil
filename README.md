## Budget Insight Ledger

^ This is the best title GPT could spit out. A very basic bookkeeping/finance tracker for personal (or small business) use. It can run standalone or in a docker container.
Stores database in json files, each project is a git repo, allowing you to undo any action and view the state of your project at any point in the past.

**The app does not collect any personal information**

### Features
- [x] grouping transactions
- [x] search-as-you-type for groups and individual payments
- [x] mobile-friendly
- [x] receipt attachments
- [x] friendly API (swagger)

### Wishlist
- [ ] time machine-like view of past states
- [ ] roll back to a previous state
- [ ] passcode authentication
- [ ] calendar view for date inputs
- [ ] migrations for database changes preserving rollback

### Run

```bash
docker run -v ./data:/app/data -p 8000:8000 builder555/bil
```

Navigate to http://localhost:8000

### Development

Prerequisites:

- node 16+
- yarn
- python 3.10+
- poetry
- libmagic
- setuptools

```bash
git clone https://github.com/builder555/bil.git

# run api:
cd bil/api
poetry install
poetry run start
# to view swagger: http://localhost:8000/docs

#run ui:
cd bil/ui
yarn install
yarn run serve
#to view ui: http://localhost:8080
```

<img width="908" alt="image" src="https://github.com/user-attachments/assets/57d4ee16-a166-4829-ab88-dab643b6a15d">

![screencap](https://github.com/user-attachments/assets/2cb7561a-dc1c-4649-9142-e4de9e3954b6)
