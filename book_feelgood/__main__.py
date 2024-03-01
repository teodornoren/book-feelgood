from book_feelgood.book import book
from book_feelgood.parse import initialize_parser

if __name__ == "__main__":
    book(**initialize_parser())
