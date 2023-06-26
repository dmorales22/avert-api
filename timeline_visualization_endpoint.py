from search_endpoint import search
import datetime

timeline_dummy_response = {
    "process": [
        {"x": 100, "y": 10, "tooltip": "hello"},
        {"x": 150, "y": 15, "tooltip": "hello"},
        {"x": 190, "y": 17, "tooltip": "hello"},
        {"x": 250, "y": 19, "tooltip": "hello"},
        {"x": 310, "y": 21, "tooltip": "hello"},
        {"x": 400, "y": 25, "tooltip": "hello"},
        {"x": 500, "y": 40, "tooltip": "hello"},
        {"x": 510, "y": 50, "tooltip": "hello"},
        {"x": 600, "y": 30, "tooltip": "hello"},
        {"x": 700, "y": 35, "tooltip": "hello"},
        {"x": 800, "y": 40, "tooltip": "hello"},
        {"x": 900, "y": 45, "tooltip": "hello"},
        {"x": 1000, "y": 47, "tooltip": "hello"},
        {"x": 1100, "y": 55, "tooltip": "hello"},
        {"x": 1230, "y": 51, "tooltip": "hello"},
        {"x": 1300, "y": 60, "tooltip": "hello"},
        {"x": 1330, "y": 65, "tooltip": "hello"},
        {"x": 1400, "y": 70, "tooltip": "hello"},
        {"x": 1450, "y": 71, "tooltip": "hello"},
        {"x": 1500, "y": 69, "tooltip": "hello"},
    ],
    "screenshot": [
        {"x": 100, "y": 25, "tooltip": "hellds"},
        {"x": 150, "y": 35, "tooltip": "hellds"},
        {"x": 190, "y": 35, "tooltip": "hellds"},
        {"x": 250, "y": 40, "tooltip": "hellds"},
        {"x": 310, "y": 45, "tooltip": "hellds"},
        {"x": 400, "y": 42, "tooltip": "hellds"},
        {"x": 500, "y": 57, "tooltip": "hellds"},
        {"x": 510, "y": 67, "tooltip": "hellds"},
        {"x": 600, "y": 40, "tooltip": "hellds"},
        {"x": 700, "y": 46, "tooltip": "hellds"},
        {"x": 800, "y": 50, "tooltip": "hellds"},
        {"x": 900, "y": 60, "tooltip": "hellds"},
        {"x": 1000, "y": 66, "tooltip": "hellds"},
        {"x": 1100, "y": 79, "tooltip": "hellds"},
        {"x": 1230, "y": 60, "tooltip": "hellds"},
        {"x": 1300, "y": 75, "tooltip": "hellds"},
        {"x": 1330, "y": 80, "tooltip": "hellds"},
        {"x": 1400, "y": 82, "tooltip": "hellds"},
        {"x": 1450, "y": 88, "tooltip": "hellds"},
        {"x": 1500, "y": 87, "tooltip": "hellds"},
    ]
}


def dbtime_to_unix_mili(time):
    date = datetime.datetime.strptime(time, '%H:%M:%ST%Y-%m-%d')
    timestamp = str(
        (date - datetime.datetime(1970, 1, 1)).total_seconds()*1000)
    return int(timestamp[:-2])


def turn_result_to_output(result, output_dictionary):
    if result['type'] not in output_dictionary:
        output_dictionary[result['type']] = len(output_dictionary) + 1

    y = output_dictionary[result['type']]

    return {
        'x': dbtime_to_unix_mili(result['timestamp']),
        'y': y,
        'tooltip': f'{result["mac_address"]}<br>{result["ip_address"]}<br>{result["description"]}'
    }


def generate_timeline_visualization(query):
    results = search(query)
    out = {}
    y_mapping = {}

    for result in results:
        if result['type'] not in out:
            out[result['type']] = []

        out[result['type']].append(turn_result_to_output(result, y_mapping))

    check = {}

    for key in out:
        check[key] = set()
        for elem in out[key]:
            check[key].add(elem['y'])

    print('CHECK')
    print(check)
    print(y_mapping)

    return out


def main():
    print(dbtime_to_unix_mili("18:50:35T2021-10-20"))


if __name__ == '__main__':
    main()
