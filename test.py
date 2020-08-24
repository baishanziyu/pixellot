from itsdangerous import Serializer
if __name__ == '__main__':
    from itsdangerous import Serializer
    s = Serializer('secret-key','36000')
    a = s.dumps({'rrr': 1})

    b = Serializer('secret-key')
    data = s.loads(a)
    print(data['rrr'])
    print(data)