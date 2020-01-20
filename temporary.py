ot = input().split("? ")
extraversion = {
    "+1": [1, 3, 8, 10, 13, 17, 22, 25, 27, 39, 44, 46, 49, 53, 56],
    "-1": [5, 15, 20, 29, 32, 34, 37, 41, 51]
}

neurotism = {
    "+1": [2, 4, 7, 9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40, 43, 45, 47, 50, 52, 55, 57]
}

lie = {
    "+1": [6, 24, 36],
    "-1": [12, 18, 30, 42, 48, 54]
}

for i in range(len(ot)):
    item = i + 1
    if item in extraversion['+1']:
        print(str(i + 1) + '. ' + str(ot[i]) + '?|extroversion|+1')
    if item in extraversion['-1']:
        print(str(i + 1) + '. ' + str(ot[i]) + '?|extroversion|-1')
    if item in neurotism['+1']:
        print(str(i + 1) + '. ' + str(ot[i]) + '?|neurotism|+1')
    if item in lie['+1']:
        print(str(i + 1) + '. ' + str(ot[i]) + '?|lie|+1')
    if item in lie['-1']:
        print(str(i + 1) + '. ' + str(ot[i]) + '?|lie|-1')
