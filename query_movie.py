import sys
import json
from llm_engine import get_llm_engine

# Set UTF-8 encoding for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

def print_movie_box_office(movie_name):
    engine = get_llm_engine()
    print(f"\n🔍 Searching Box Office & AI Financials for: '{movie_name}'...")
    result = engine.query_movie(movie_name)
    
    if not result or 'movie' not in result:
        print(f"❌ Could not retrieve data for '{movie_name}'.")
        return

    m = result['movie']
    source = result.get('source', 'AI Intelligence Engine')
    
    print("\n" + "=" * 70)
    print(f" 🎬  {m.get('title', movie_name).upper()} ({m.get('release_year', 'N/A')})")
    print("=" * 70)
    print(f" 🏆 Commercial Verdict : {m.get('verdict', 'N/A')}")
    if m.get('local_currency_note'):
        print(f" 💰 Local Box Office   : {m.get('local_currency_note')}")
    print(f" 🌍 Worldwide Gross    : ${m.get('worldwide_gross', 0):,}")
    print(f" 💵 Production Budget  : ${m.get('budget', 0):,}")
    print(f" 📈 ROI Multiplier     : {m.get('profit_multiplier', 0)}x ({m.get('roi_percentage', 0)}% Return)")
    print(f" 🇺🇸 Domestic Gross     : ${m.get('domestic_gross', 0):,}")
    print(f" 🌐 Overseas Gross     : ${m.get('international_gross', 0):,}")
    print(f" 📣 Director           : {m.get('director', 'N/A')}")
    print(f" 🌟 Top Cast           : {', '.join(m.get('top_cast', []))}")
    print(f" 🏷️  Genres             : {', '.join(m.get('genres', []))}")
    print("-" * 70)
    print(f" 📖 Synopsis:\n    {m.get('synopsis', 'N/A')}")
    print("-" * 70)
    print(f" 📊 Financial Breakdown:\n    {m.get('financial_breakdown', 'N/A')}")
    print("-" * 70)
    if m.get('key_success_factors'):
        print(" 🎯 Key Success Factors:")
        for factor in m.get('key_success_factors', []):
            print(f"    • {factor}")
        print("-" * 70)
    if m.get('fun_fact'):
        print(f" 💡 Trivia Fact:\n    {m.get('fun_fact')}")
        print("-" * 70)
    print(f" ℹ️  Data Source: {source}\n")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        movie_query = " ".join(sys.argv[1:])
        print_movie_box_office(movie_query)
    else:
        print("\n=== CineMetric AI - Terminal Movie Box Office Query ===")
        while True:
            try:
                user_input = input("\nEnter a movie title (or 'exit' to quit): ").strip()
                if not user_input or user_input.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                print_movie_box_office(user_input)
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break
