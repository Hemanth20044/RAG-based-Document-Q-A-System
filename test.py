from rag_engine import load_document, build_vectorstore, build_qa_chain, ask_question

class FakeFile:
    name = "test.pdf"
    def getvalue(self):
        with open("test.pdf", "rb") as f:
            return f.read()