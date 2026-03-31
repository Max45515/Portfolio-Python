# Простая сортировка (попросил ИИ проверить на ошибки (в целом код рабочий но его можно улучшить) получилось то что ниже)

arr = list(map(int, input("Введите числа через пробел: ").split()))

n = len(arr)

for j in range(n):
    for i in range(n - 1):
        if arr[i] < arr[i + 1]:
            arr[i], arr[i + 1] = arr[i + 1], arr[i]

print(arr)
