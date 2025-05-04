import copy
from datetime import date
#
# def box_in_truck(empty_truck, non_empty_truck, boxes, truck, box):
#     if len(truck["free_space"]) >= len(box["size"]):
#         for spot in truck["free_space"]:
#             for i in range(2):
#                 flag = False
#                 free_space = truck["free_space"].copy()
#                 if i == 0:
#                     for dot in box["size"]:
#                         if [spot[0] + dot[0], spot[1] + dot[1]] in truck["free_space"]:
#                             free_space.remove([spot[0] + dot[0], spot[1] + dot[1]])
#                         else:
#                             break
#                     else:
#                         flag = True
#                 if i == 1 and box["turn_permission"] and box["size"][-1][0] != box["size"][-1][1]:
#                     for dot in box["size"]:
#                         if [spot[0] + dot[1], spot[1] + dot[0]] in truck["free_space"]:
#                             free_space.remove([spot[0] + dot[1], spot[1] + dot[0]])
#                         else:
#                             break
#                     else:
#                         flag = True
#                 if flag:
#                     empty_truck_copy = copy.deepcopy(empty_truck)
#                     non_empty_truck_copy = copy.deepcopy(non_empty_truck)
#                     boxes_copy = copy.deepcopy(boxes)
#                     truck_copy = copy.deepcopy(truck)
#                     truck_copy["free_space"] = free_space.copy()
#                     truck_copy["order_id"].append(boxes_copy[0]["id"])
#                     boxes_copy[0]["truck_id"] = truck_copy["id"]
#                     non_empty_truck_copy.append(truck_copy)
#                     param = boxes_in_trucks(empty_truck_copy, non_empty_truck_copy, boxes_copy[1:])
#                     if param[-1]:
#                         param[2].append(boxes_copy[0])
#                         return param
#     return [False]
#
# def boxes_in_trucks(empty_truck, non_empty_truck, boxes):
#     if not boxes:
#         return [empty_truck, non_empty_truck, boxes, True]
#     for index_truck in range(len(non_empty_truck)):
#         param = box_in_truck(empty_truck, non_empty_truck[:index_truck]+non_empty_truck[index_truck+1:], boxes, non_empty_truck[index_truck], boxes[0])
#         if param[-1]:
#             return param
#     checked_sizes = []
#     for index_truck in range(len(empty_truck)):
#         if empty_truck[index_truck]["size"] in checked_sizes:
#             continue
#         param = box_in_truck(empty_truck[:index_truck]+empty_truck[index_truck+1:], non_empty_truck, boxes, empty_truck[index_truck], boxes[0])
#         if param[-1]:
#             return param
#         checked_sizes.append(empty_truck[index_truck]["size"])
#     return [False]







def box_in_truck_money(empty_truck, non_empty_truck, boxes, boxes_in_truck, truck, box, money, money_search, config):
    if len(truck["free_space"]) >= len(box["size"]):
        for spot in truck["free_space"]:
            for i in range(2):
                flag = False
                free_space = truck["free_space"].copy()
                if i == 0:
                    for dot in box["size"]:
                        if [spot[0] + dot[0], spot[1] + dot[1]] in truck["free_space"]:
                            free_space.remove([spot[0] + dot[0], spot[1] + dot[1]])
                        else:
                            break
                    else:
                        flag = True
                if i == 1 and box["turn_permission"] and box["size"][-1][0] != box["size"][-1][1]:
                    for dot in box["size"]:
                        if [spot[0] + dot[1], spot[1] + dot[0]] in truck["free_space"]:
                            free_space.remove([spot[0] + dot[1], spot[1] + dot[0]])
                        else:
                            break
                    else:
                        flag = True
                if flag:
                    if not truck["order_id"]:
                        money_copy = money + truck["money"]
                    else:
                        money_copy = money
                    if not config or money_copy < config[-2]:
                        empty_truck_copy = copy.deepcopy(empty_truck)
                        non_empty_truck_copy = copy.deepcopy(non_empty_truck)
                        boxes_copy = copy.deepcopy(boxes)
                        boxes_in_truck_copy = copy.deepcopy(boxes_in_truck)
                        truck_copy = copy.deepcopy(truck)
                        truck_copy["free_space"] = free_space.copy()
                        truck_copy["order_id"].append(boxes_copy[0]["id"])
                        boxes_copy[0]["truck_id"] = truck_copy["id"]
                        boxes_in_truck_copy.append(boxes_copy[0])
                        non_empty_truck_copy.append(truck_copy)
                        config = boxes_in_trucks_money(empty_truck_copy, non_empty_truck_copy, boxes_copy[1:],
                                                       boxes_in_truck_copy, money_copy, money_search, config)
                        if config and not config[-1]:
                            return config
    return config

def boxes_in_trucks_money(empty_truck, non_empty_truck, boxes, boxes_in_truck, money, money_search, config):
    if not boxes:
        if not config:
            config = [empty_truck, non_empty_truck, boxes, boxes_in_truck, money, money_search]
        else:
            if config[-2] > money:
                config = [empty_truck, non_empty_truck, boxes, boxes_in_truck, money, money_search]
        return config
    for index_truck in range(len(non_empty_truck)):
        config = box_in_truck_money(empty_truck, non_empty_truck[:index_truck]+non_empty_truck[index_truck+1:], boxes, boxes_in_truck, non_empty_truck[index_truck], boxes[0], money, money_search, config)
    checked_sizes = []
    for index_truck in range(len(empty_truck)):
        if empty_truck[index_truck]["size"] in checked_sizes:
            continue
        config = box_in_truck_money(empty_truck[:index_truck]+empty_truck[index_truck+1:], non_empty_truck, boxes, boxes_in_truck, empty_truck[index_truck], boxes[0], money, money_search, config)
        checked_sizes.append(empty_truck[index_truck]["size"])
    return config








truck = [
    {
        "id": 0,
        "size_x": 1,
        "size_y": 1,
        "money": 1
    },
{
        "id": 1,
        "size_x": 3,
        "size_y": 3,
        "money": 5
    },
{
        "id": 2,
        "size_x": 1,
        "size_y": 1,
        "money": 1
    },
]
order = [
    {
        "id": 0,
        "size_x": 1,
        "size_y": 1,
        "turn_permission": True,
        "due_date": date(1000, 1,7)
    },
{
        "id": 1,
        "size_x": 1,
        "size_y": 1,
        "turn_permission": True,
        "due_date": date(1000, 1,5)
    },
{
        "id": 2,
        "size_x": 3,
        "size_y": 3,
        "turn_permission": True,
        "due_date": date(1000, 1,9)
    },
]
truck_data = []
order_data = []
for i in truck:
    truck_data.append({
        "id": i["id"],
        "free_space": [[x, y] for x in range(i["size_x"]) for y in range(i["size_y"])],
        "order_id": [],
        "size": [i["size_x"], i["size_y"]],
        "money": i["money"]
    })
for i in order:
    order_data.append({
        "id": i["id"],
        "size": [[x, y] for x in range(i["size_x"]) for y in range(i["size_y"])],
        "turn_permission": i["turn_permission"],
        "date": i["due_date"],
        "truck_id": -1
    })
order_data.sort(key=lambda x: x["date"])
order_to_sort = order_data.copy()
order_in_truck = []
doesnt_fit = []
empty_truck = truck_data.copy()
non_empty_truck = []
empty_truck_temp = copy.deepcopy(empty_truck)
non_empty_truck_temp = copy.deepcopy(non_empty_truck)

for i in (truck, order, truck_data, order_data, order_to_sort, order_in_truck, doesnt_fit, empty_truck, non_empty_truck):
    print(f"do {i} \n")


for box in order_to_sort:
    config = boxes_in_trucks_money(empty_truck_temp, non_empty_truck_temp, [box], order_in_truck, 0, False, [])
    if config:
        empty_truck_temp = config[0]
        non_empty_truck_temp = config[1]
        order_in_truck = config[3]
        continue
    else:
        print("rfrrhrj")
        empty_truck_copy = copy.deepcopy(empty_truck)
        non_empty_truck_copy = copy.deepcopy(non_empty_truck)
        config = boxes_in_trucks_money(empty_truck_copy, non_empty_truck_copy, order_in_truck+[box], [], 0, False, [])
        if config:
            empty_truck_temp = config[0]
            non_empty_truck_temp = config[1]
            order_in_truck = config[3]
            continue
        else:
            doesnt_fit.append(box)

for i in (order_in_truck, doesnt_fit, empty_truck_temp, non_empty_truck_temp):
    print(f"\nposle {i}")

empty_truck_copy = copy.deepcopy(empty_truck)
non_empty_truck_copy = copy.deepcopy(non_empty_truck)
config = boxes_in_trucks_money(empty_truck_copy, non_empty_truck_copy, order_in_truck, [], 0, True, [])
for i in config:
    print(f"\nmoney {i}")



