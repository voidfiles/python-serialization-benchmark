from subjects import marsh, rf, serp, strain, col, hand
from data import ParentTestObject

TARGET = {
    'foo': 'bar',
    'bar': 5,
    'sub': {'w': 100, 'y': 'hello', 'z': 10, 'x': 30},
    'subs': [
        {'w': 100, 'y': 'hello', 'z': 10, 'x': 30},
        {'w': 1000, 'y': 'hello', 'z': 10, 'x': 30},
        {'w': 2000, 'y': 'hellohello', 'z': 20, 'x': 50},
        {'w': 3000, 'y': 'hellohellohello', 'z': 30, 'x': 70},
        {'w': 4000, 'y': 'hellohellohellohello', 'z': 40, 'x': 90},
        {'w': 5000, 'y': 'hellohellohellohellohello', 'z': 50, 'x': 110},
        {'w': 6000, 'y': 'hellohellohellohellohellohello', 'z': 60, 'x': 130},
        {'w': 7000, 'y': 'hellohellohellohellohellohellohello', 'z': 70, 'x': 150},
        {
            'w': 8000,
            'y': 'hellohellohellohellohellohellohellohello',
            'z': 80,
            'x': 170,
        }, {
            'w': 9000,
            'y': 'hellohellohellohellohellohellohellohellohello',
            'z': 90,
            'x': 190,
        }
    ]
}


def test_serializers():
    test_object = ParentTestObject()

    for subject in (rf, marsh, serp, strain, col, hand):
        print subject.__name__
        data = subject.serialization_func(test_object, False)
        assert data['foo'] == TARGET['foo']
        assert data['bar'] == TARGET['bar']
        assert data['sub']['w'] == TARGET['sub']['w']
        assert data['subs'][3]['y'] == TARGET['subs'][3]['y']
        assert data['subs'][3]['x'] == TARGET['subs'][3]['x']

        datas = subject.serialization_func([test_object, test_object], True)
        for data in datas:
            assert data['foo'] == TARGET['foo']
            assert data['sub']['w'] == TARGET['sub']['w']
            assert data['subs'][3]['y'] == TARGET['subs'][3]['y']
            assert data['subs'][3]['x'] == TARGET['subs'][3]['x']
