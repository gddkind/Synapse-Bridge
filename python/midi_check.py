import mido

print("=== Portas MIDI Disponíveis ===")
print("\n[Entradas / Inputs]:")
for name in mido.get_input_names():
    print(f" - {name}")

print("\n[Saídas / Outputs]:")
for name in mido.get_output_names():
    print(f" - {name}")

print("\n===============================")
print("Verifique se as portas 'Band ...' aparecem acima.")
