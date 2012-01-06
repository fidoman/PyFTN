with recursive allsubscription(target, dir) as (
  select target, 1 from subscriptions where subscriber=536
  Union
  select a.id, 0 from allsubscription s, addresses a.
  where a.group = s.target.
  and (select count(id) from subscriptions where target=a.id) = 0
    )
  select sa.domain, sa.text, dir
  from allsubscription alls, addresses sa
  where sa.id=alls.target and sa.domain=1
  order by dir, text
;
