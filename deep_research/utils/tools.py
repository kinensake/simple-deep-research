from langchain_tavily import TavilySearch

search_tool = TavilySearch(max_results=3, include_raw_content=False)
