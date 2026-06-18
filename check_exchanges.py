# ==============================================================================
# Developed by Ben Timothy
# App Name: CCXT Full Exchange Compatibility Verifier
# Description: Validates local network connectivity and tests ALL supported 
#              exchange routing drivers available within the native CCXT library.
# ==============================================================================

import ccxt
import sys

def main():
    print("=" * 70)
    print(" CCXT FULL NETWORK & EXCHANGE DRIVER VERIFIER")
    print("=" * 70)
    
    # 1. Check CCXT Version
    print(f"[+] Native CCXT Version: {ccxt.__version__}")
    
    # 2. Get total available exchanges in this CCXT version
    all_exchanges = ccxt.exchanges
    total_exchanges = len(all_exchanges)
    print(f"[+] Total built-in exchange drivers detected: {total_exchanges}")
    print("[-] Starting comprehensive test for all available exchanges...")
    print("[-] Note: This may take a few minutes depending on your connection.")
    print("=" * 70)
    
    success_exchanges = []
    failed_count = 0
    
    # 3. Iterate and test every single exchange in CCXT
    for index, ex in enumerate(all_exchanges, 1):
        print(f"[{index}/{total_exchanges}] Testing gateway '{ex}'... ", end="", flush=True)
        try:
            # Dynamically fetch the exchange class
            exchange_class = getattr(ccxt, ex)
            # Initialize with a strict timeout to keep the loop moving efficiently
            exchange_instance = exchange_class({
                'timeout': 5000,
                'enableRateLimit': True
            })
            
            # Execute a live market structure network handshake
            exchange_instance.load_markets()
            print("SUCCESS")
            success_exchanges.append(ex)
        except Exception:
            print("FAILED")
            failed_count += 1
            
    # 4. Render Final Summary Matrix
    print("\n" + "=" * 70)
    print(" VERIFICATION SUMMARY REPORT")
    print("=" * 70)
    print(f"  - Total Exchanges Scanned : {total_exchanges}")
    print(f"  - Successful Connections  : {len(success_exchanges)}")
    print(f"  - Failed/Blocked Gateways : {failed_count}")
    print("=" * 70)
    
    if success_exchanges:
        print("\n[i] Verified Operational Gateways (Safe to use in your .env file):")
        # Print the successful exchanges in a clean wrapped format
        columns = 4
        for i in range(0, len(success_exchanges), columns):
            row = success_exchanges[i:i+columns]
            print("    " + "".join(ex.ljust(18) for ex in row))
            
        print("\n[SUGGESTION]")
        print(f"  You can safely replace CCXT_EXCHANGE in your .env with any name listed above.")
        print(f"  Example layout: CCXT_EXCHANGE=\"{success_exchanges[0]}\"")
    else:
        print("\n[CRITICAL ERROR] All network connection attempts failed.")
        print("  Your local machine or ISP firewall seems to be entirely restricting outbound financial API routing.")
        print("  Recommendation: Please consider configuring a VPN or adding system proxies before retrying.")
        
    print("=" * 70)

if __name__ == "__main__":
    main()