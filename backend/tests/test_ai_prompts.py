import asyncio
import sys
import os
from dotenv import load_dotenv

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env variables so GROQ_API_KEY is available (from project root)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(project_root, '.env'))

from ai_agent import process_chat

async def run_tests():
    print("="*50)
    print("Mulai Pengujian Prompt AI Agent (Chatbot)")
    print("="*50)

    # 1. Test Report Lost Item
    prompt1 = "Saya kehilangan laptop Asus ROG warna hitam di perpustakaan lantai 2 kemarin sore. Nama saya Budi."
    print(f"\n[1] PROMPT: {prompt1}")
    response1, tools1 = await process_chat(prompt1)
    print(f"RESPONSE:\n{response1}")
    print(f"TOOLS USED: {tools1}")

    # 2. Test Report Found Item
    prompt2 = "Saya Andi, saya menemukan sebuah kunci motor Honda di parkiran motor timur."
    print(f"\n[2] PROMPT: {prompt2}")
    response2, tools2 = await process_chat(prompt2)
    print(f"RESPONSE:\n{response2}")
    print(f"TOOLS USED: {tools2}")

    # 3. Test Search Item
    prompt3 = "Tolong carikan apakah ada yang melaporkan kehilangan kunci motor Honda?"
    print(f"\n[3] PROMPT: {prompt3}")
    response3, tools3 = await process_chat(prompt3)
    print(f"RESPONSE:\n{response3}")
    print(f"TOOLS USED: {tools3}")

    # 4. Test Update Item
    prompt4 = "Saya Budi, ingin mengupdate laporan kehilangan laptop saya, warnanya abu-abu bukan hitam."
    print(f"\n[4] PROMPT: {prompt4}")
    response4, tools4 = await process_chat(prompt4)
    print(f"RESPONSE:\n{response4}")
    print(f"TOOLS USED: {tools4}")

    # 5. Test Update Item dengan Kode Unik
    prompt5 = "Tolong update laporan barang dengan kode ITK-12345, lokasinya ternyata di gedung B."
    print(f"\n[5] PROMPT: {prompt5}")
    response5, tools5 = await process_chat(prompt5)
    print(f"RESPONSE:\n{response5}")
    print(f"TOOLS USED: {tools5}")

    # 6. Test Delete Item
    prompt6 = "Tolong hapus laporan barang dengan kode ITK-12345 karena barangnya sudah ketemu."
    print(f"\n[6] PROMPT: {prompt6}")
    response6, tools6 = await process_chat(prompt6)
    print(f"RESPONSE:\n{response6}")
    print(f"TOOLS USED: {tools6}")

if __name__ == "__main__":
    asyncio.run(run_tests())
