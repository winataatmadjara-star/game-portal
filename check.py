from app import create_app

app = create_app()

print("=== DAFTAR ROUTE ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
    print(f"{sorted(rule.methods)}  {rule}")