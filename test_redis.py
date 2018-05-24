import redis

r = redis.Redis(host='192.168.100.198', port=6379, password='!QE%^E2sdf23RGF@ml239', db=0)
print(r.dbsize())
print(r.get('package'))

r = redis.Redis(host='192.168.100.198', port=6379, password='!QE%^E2sdf23RGF@ml239', db=13)
print(r.dbsize())
print(r.hget('event_order_advance_008aea6a62115ec4923829ee09f76a9c18243f5d', 'user'))
