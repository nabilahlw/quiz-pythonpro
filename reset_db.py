"""
Script untuk reset database dan melihat semua user
Gunakan ini jika ada masalah dengan database
"""

from database import reset_database, get_all_users, init_db
import os

def main():
    print("\n" + "="*50)
    print("🔧 DATABASE MANAGEMENT TOOL")
    print("="*50)
    
    print("\n1. Lihat semua user")
    print("2. Reset database (HAPUS SEMUA DATA)")
    print("3. Keluar")
    
    choice = input("\nPilih opsi (1-3): ").strip()
    
    if choice == "1":
        print("\n📋 Menampilkan semua user...")
        users = get_all_users()
        if not users:
            print("❌ Database kosong atau error!")
        
    elif choice == "2":
        confirm = input("\n⚠️  PERINGATAN: Ini akan menghapus SEMUA data!\nKetik 'RESET' untuk konfirmasi: ")
        if confirm == "RESET":
            reset_database()
            print("✅ Database berhasil direset!")
        else:
            print("❌ Reset dibatalkan")
    
    elif choice == "3":
        print("👋 Keluar...")
    
    else:
        print("❌ Pilihan tidak valid!")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()