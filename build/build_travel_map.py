#!/usr/bin/env python3
"""
Build travel-map.html from template + live GeoJSON data.
Fetches administrative boundaries from DataV.GeoAtlas API,
injects them into the HTML template, and writes the output.
"""
import json, os, ssl, urllib.request, time

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE

def fetch_geo(adcode, level="sub"):
    url = f"https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_{level}.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30, context=_CTX) as resp:
        return json.loads(resp.read())


def simplify_coords(coords, precision=3):
    """Round coordinates to reduce file size."""
    if isinstance(coords[0], (int, float)):
        return [round(c, precision) for c in coords]
    return [simplify_coords(c, precision) for c in coords]


def simplify_geo(geojson):
    for f in geojson.get("features", []):
        g = f.get("geometry", {})
        if "coordinates" in g:
            g["coordinates"] = simplify_coords(g["coordinates"])
    return geojson


# ── 1. Fetch province-level (11 cities) ──
print("Fetching Zhejiang province boundaries...")
province_geo = fetch_geo(330000, "full")
print(f"  -> {len(province_geo['features'])} city features")

city_adcodes = {}
for f in province_geo["features"]:
    name = f["properties"]["name"]
    adcode = f["properties"]["adcode"]
    city_adcodes[name] = adcode
    print(f"    {name}: adcode={adcode}")

# ── 2. Fetch city-level (districts) for each city ──
print("\nFetching district boundaries for each city...")
city_geos = {}
for name, adcode in city_adcodes.items():
    print(f"  Fetching {name} ({adcode})...")
    try:
        data = fetch_geo(adcode, "full")
        city_geos[name] = data
        print(f"    -> {len(data['features'])} districts")
    except Exception as e:
        print(f"    x Failed: {e}")
        city_geos[name] = {"type": "FeatureCollection", "features": []}
    time.sleep(0.3)  # rate limit

# ── 3. Simplify GeoJSON (reduce coordinate precision) ──
province_geo = simplify_geo(province_geo)
for name in city_geos:
    city_geos[name] = simplify_geo(city_geos[name])

# ── 4. Travel data ──
travel_data = [
  {"id":"hangzhou","name":"杭州市","adcode":330100,"desc":"浙江省会，\u201c上有天堂下有苏杭\u201d的人间天堂。西湖、龙井茶、互联网之都，古今交融的魅力之城。","attractions":["西湖","灵隐寺","千岛湖","西溪湿地","宋城","河坊街"],"food":["西湖醋鱼","龙井虾仁","东坡肉","片儿川","葱包桧"],"districts":[
    {"name":"上城区","att":["西湖景区","南宋御街","河坊街","城隍阁","清河坊"],"food":["西湖醋鱼","葱包桧","定胜糕","知味观小笼"]},
    {"name":"拱墅区","att":["京杭大运河","拱宸桥","小河直街","香积寺","运河天地"],"food":["小河菜场美食","老桥头面馆"]},
    {"name":"西湖区","att":["灵隐寺","飞来峰","西溪湿地","龙井茶园","九溪十八涧","宋城"],"food":["龙井虾仁","西湖莼菜汤"]},
    {"name":"滨江区","att":["钱塘江畔","星光大道","物联网小镇","樱花跑道"],"food":["滨江夜市","龙湖天街美食"]},
    {"name":"萧山区","att":["湘湖","跨湖桥遗址","杭州乐园","钱江世纪城","航坞山"],"food":["萧山萝卜干","霉干菜扣肉"]},
    {"name":"余杭区","att":["良渚古城遗址","径山寺","超山梅花","塘栖古镇","梦想小镇"],"food":["径山茶","塘栖枇杷"]},
    {"name":"临平区","att":["超山风景区","临平山","运河\u00b7塘栖古镇","艺尚小镇"],"food":["临平红烧羊肉","粢毛肉圆"]},
    {"name":"钱塘区","att":["下沙高教园区","金沙湖","钱塘江海塘","大江东湿地"],"food":["下沙美食街","钱塘江鲜"]},
    {"name":"富阳区","att":["富春江","龙门古镇","黄公望隐居地","野生动物世界"],"food":["富阳土鸡","东坞山豆腐皮"]},
    {"name":"临安区","att":["天目山","大明山","太湖源","青山湖绿道","浙西大峡谷"],"food":["临安山核桃","天目笋干"]},
    {"name":"桐庐县","att":["瑶琳仙境","严子陵钓台","富春江小三峡","深澳古村"],"food":["桐庐米果","油沸馒头"]},
    {"name":"淳安县","att":["千岛湖","梅峰岛","森林氧吧","芹川古村","文渊狮城"],"food":["千岛湖鱼头","淳安米羹"]},
    {"name":"建德市","att":["新安江","七里扬帆","灵栖洞","严州古城","大慈岩"],"food":["建德豆腐包","严州干菜鸭"]}
  ]},
  {"id":"ningbo","name":"宁波市","adcode":330200,"desc":"东海之滨的港口名城，海上丝绸之路起点。书藏古今、港通天下，海鲜美食令人垂涎。","attractions":["天一阁","东钱湖","溪口","老外滩","象山影视城"],"food":["宁波汤圆","红膏呛蟹","雪菜大黄鱼","宁波烤菜"],"districts":[
    {"name":"海曙区","att":["天一阁","月湖公园","南塘老街","鼓楼","天一广场"],"food":["宁波汤圆","南塘老街小吃"]},
    {"name":"江北区","att":["老外滩","慈城古镇","保国寺","达人村"],"food":["慈城年糕","江北海鲜"]},
    {"name":"北仑区","att":["九峰山","洋沙山","梅山湾","港口博物馆","凤凰山主题乐园"],"food":["北仑海鲜","梅山鱼鲞"]},
    {"name":"镇海区","att":["招宝山","郑氏十七房","宁波帮博物馆","九龙湖"],"food":["镇海蟹糊","十七房美食"]},
    {"name":"鄞州区","att":["东钱湖","天童寺","阿育王寺","南宋石刻公园","罗蒙环球城"],"food":["东钱湖鱼鲜","鄞州麻糍"]},
    {"name":"奉化区","att":["溪口","雪窦山","蒋氏故居","滕头村","千丈岩瀑布"],"food":["奉化芋艿头","千层饼","水蜜桃"]},
    {"name":"余姚市","att":["河姆渡遗址","四明山","丹山赤水","龙泉山","天下玉苑"],"food":["余姚杨梅","梁弄大糕"]},
    {"name":"慈溪市","att":["上林湖越窑遗址","鸣鹤古镇","杭州湾湿地公园","达蓬山"],"food":["慈溪杨梅","龙山黄泥螺"]},
    {"name":"象山县","att":["象山影视城","松兰山","中国渔村","石浦古城","花岙岛"],"food":["象山海鲜","石浦鱼丸","海鲜面"]},
    {"name":"宁海县","att":["前童古镇","天河景区","宁海森林温泉","伍山石窟","许家山石头村"],"food":["宁海麦饼","望海茶"]}
  ]},
  {"id":"wenzhou","name":"温州市","adcode":330300,"desc":"中国民营经济的摇篮，山水奇秀的瓯越大地。楠溪江、雁荡山，山水诗的发源地。","attractions":["雁荡山","楠溪江","江心屿","南麂列岛"],"food":["温州鱼丸","灯盏糕","鸭舌","猪脏粉","糯米饭"],"districts":[
    {"name":"鹿城区","att":["江心屿","五马街","南塘街","江心寺","中山公园"],"food":["灯盏糕","猪脏粉","鱼丸"]},
    {"name":"龙湾区","att":["瑶溪","永昌堡","大罗山","奥体中心"],"food":["龙湾鱼饼","状元糕"]},
    {"name":"瓯海区","att":["泽雅","仙岩","大罗山","温州乐园","三垟湿地"],"food":["瓯海素面","泽雅豆腐"]},
    {"name":"洞头区","att":["半屏山","仙叠岩","望海楼","东岙沙滩","鹿西岛"],"food":["洞头海鲜","鱼饼","鮸鱼丸"]},
    {"name":"瑞安市","att":["花岩国家森林公园","玉海楼","寨寮溪","圣井山"],"food":["瑞安扎羊","湖岭牛肉"]},
    {"name":"乐清市","att":["雁荡山","中雁荡山","灵山","乐清湾","铁定溜溜"],"food":["乐清海鲜","雁荡山香螺"]},
    {"name":"永嘉县","att":["楠溪江","石桅岩","狮子岩","苍坡古村","丽水街"],"food":["楠溪江麦饼","溪鱼","素面"]},
    {"name":"平阳县","att":["南雁荡山","南麂列岛","顺溪古屋","腾蛟温泉"],"food":["平阳炒粉干","南麂大黄鱼"]},
    {"name":"文成县","att":["百丈漈","刘基故里","铜铃山","飞云湖","龙麒源"],"food":["文成粉丝","伯温家宴"]},
    {"name":"泰顺县","att":["氡泉","乌岩岭","仕水碇步","廊桥文化园","塔头底古村"],"food":["泰顺绿豆腐","米面层","肉丸"]}
  ]},
  {"id":"jiaxing","name":"嘉兴市","adcode":330400,"desc":"鱼米之乡、丝绸之府。南湖红船、烟雨江南，古镇群落的诗意栖居地。","attractions":["南湖","西塘","乌镇","盐官古镇","月河古街"],"food":["粽子","南湖菱","文虎酱鸭","海宁缸肉"],"districts":[
    {"name":"南湖区","att":["南湖","南湖革命纪念馆","月河古街","梅湾街","壕股塔"],"food":["五芳斋粽子","南湖菱","文虎酱鸭"]},
    {"name":"秀洲区","att":["王江泾运河","新塍古镇","秀湖公园","莲泗荡"],"food":["新塍月饼","秀洲粽"]},
    {"name":"海宁市","att":["盐官观潮","海宁皮革城","王国维故居","硖石灯彩","百里钱塘"],"food":["海宁缸肉","长安宴球","海宁粉皮"]},
    {"name":"平湖市","att":["东湖","莫氏庄园","九龙山","南河头历史街区"],"food":["平湖糟蛋","平湖西瓜","杜瓜籽"]},
    {"name":"桐乡市","att":["乌镇","丰子恺故居","福严寺","崇福古镇"],"food":["桐乡羊肉面","姑嫂饼","杭白菊"]},
    {"name":"嘉善县","att":["西塘","碧云花园","大云温泉","汾湖"],"food":["西塘八珍糕","管老太臭豆腐"]},
    {"name":"海盐县","att":["南北湖","绮园","天宁寺","秦山核电站科技馆"],"food":["海盐大头菜","澉浦羊肉"]}
  ]},
  {"id":"huzhou","name":"湖州市","adcode":330500,"desc":"南太湖明珠，\u201c行遍江南清丽地，人生只合住湖州\u201d。绿水青山就是金山银山的发源地。","attractions":["南浔古镇","莫干山","安吉竹海","太湖","中南百草园"],"food":["千张包","湖州大馄饨","安吉白茶","练市酱羊肉"],"districts":[
    {"name":"吴兴区","att":["飞英塔","铁佛寺","衣裳街","妙西原乡小镇","西山漾湿地"],"food":["千张包","湖州大馄饨","诸老大粽子"]},
    {"name":"南浔区","att":["南浔古镇","小莲庄","嘉业堂藏书楼","百间楼","荻港古村"],"food":["双交面","桔红糕","浔蹄"]},
    {"name":"德清县","att":["莫干山","下渚湖湿地","新市古镇","劳岭村洋家乐"],"food":["新市茶糕","防风神仙鸡","德清笋干"]},
    {"name":"长兴县","att":["中国扬子鳄村","仙山湖","大唐贡茶院","八都岕十里银杏长廊"],"food":["长兴干挑面","紫笋茶","长兴白果"]},
    {"name":"安吉县","att":["中国大竹海","藏龙百瀑","天荒坪","HelloKitty乐园","余村"],"food":["安吉白茶","百笋宴","安吉山核桃"]}
  ]},
  {"id":"shaoxing","name":"绍兴市","adcode":330600,"desc":"名士之乡、黄酒之都。鲁迅故里、兰亭雅集，一座没有围墙的博物馆。","attractions":["鲁迅故里","兰亭","沈园","东湖","安昌古镇"],"food":["茴香豆","绍兴黄酒","霉干菜焖肉","臭豆腐","奶油小攀"],"districts":[
    {"name":"越城区","att":["鲁迅故里","沈园","兰亭","东湖","大禹陵","仓桥直街"],"food":["茴香豆","臭豆腐","奶油小攀","霉干菜焖肉"]},
    {"name":"柯桥区","att":["柯岩","鉴湖","安昌古镇","鲁镇","兰亭国家森林公园"],"food":["安昌腊肠","绍兴黄酒","霉苋菜梗"]},
    {"name":"上虞区","att":["曹娥庙","覆卮山","中华孝德园","白马湖","凤鸣山"],"food":["上虞葡萄","盖北野藤葡萄","谢塘豆腐干"]},
    {"name":"诸暨市","att":["五泄飞瀑","西施故里","汤江岩","白塔湖国家湿地"],"food":["诸暨次坞打面","西施豆腐","同山烧"]},
    {"name":"嵊州市","att":["崇仁古镇","百丈飞瀑","王羲之故居","越剧博物馆"],"food":["嵊州小笼包","炒年糕","榨面"]},
    {"name":"新昌县","att":["大佛寺","穿岩十九峰","沃洲湖","天姥山","达利丝绸世界"],"food":["新昌小京生","春饼","芋饺"]}
  ]},
  {"id":"jinhua","name":"金华市","adcode":330700,"desc":"浙江之心，历史文化名城。金华火腿闻名天下，横店影视城造梦东方。","attractions":["双龙洞","横店影视城","诸葛八卦村","古子城","牛头山"],"food":["金华火腿","金华酥饼","兰溪鸡子粿","东阳沃面"],"districts":[
    {"name":"婺城区","att":["双龙洞","古子城","太平天国侍王府","金华山"],"food":["金华酥饼","金华煲","冷淘"]},
    {"name":"金东区","att":["艾青故居","琐园古村","金华山旅游经济区","坡阳老街"],"food":["金东桶饼","源东白桃"]},
    {"name":"兰溪市","att":["诸葛八卦村","地下长河","六洞山","游埠古镇"],"food":["鸡子粿","兰溪牛肉面","兰江蟹黄汤包"]},
    {"name":"义乌市","att":["义乌国际商贸城","佛堂古镇","双林寺","德胜岩"],"food":["义乌拉面","东河肉饼","红糖麻花"]},
    {"name":"东阳市","att":["横店影视城","卢宅","中国木雕城","秦王宫","明清宫苑"],"food":["东阳沃面","东阳火腿","童子蛋"]},
    {"name":"永康市","att":["方岩","永康五金城","石鼓寮","飞龙山"],"food":["永康肉麦饼","鹅肥肝","十八腔"]},
    {"name":"浦江县","att":["仙华山","郑义门","嵩溪古村","水晶小镇"],"food":["浦江麦饼","豆腐皮","牛清汤"]},
    {"name":"武义县","att":["牛头山","熟溪廊桥","郭洞古生态村","俞源太极星象村"],"food":["武义醋鸡","宣平馄饨","竹筒饭"]},
    {"name":"磐安县","att":["花溪","百丈潭","十八涡","磐安药膳馆","管头村"],"food":["磐安药膳","香菇","玉山古茶场"]}
  ]},
  {"id":"quzhou","name":"衢州市","adcode":330800,"desc":"南孔圣地、浙江绿肺。四省通衢，生态绝佳，一座最具幸福感的江南小城。","attractions":["江郎山","廿八都","龙游石窟","孔氏南宗家庙","根宫佛国"],"food":["衢州三头一掌","龙游发糕","开化气糕","常山贡面"],"districts":[
    {"name":"柯城区","att":["孔氏南宗家庙","水亭门历史街区","鹿鸣山","九华妙境"],"food":["衢州兔头","衢州鸭头","烤饼"]},
    {"name":"衢江区","att":["药王山","紫微山","湖南镇大坝","全旺镇"],"food":["衢江土鸡","廿里面条"]},
    {"name":"江山市","att":["江郎山","廿八都古镇","仙霞关","清漾毛氏文化村"],"food":["江山米糕","风炉仔炖菜","铜锣糕"]},
    {"name":"龙游县","att":["龙游石窟","龙游民居苑","六春湖","溪口古镇"],"food":["龙游发糕","龙游小辣椒","龙游馒头"]},
    {"name":"常山县","att":["三衢石林","中国观赏石博览园","梅树底景区","长风渔村"],"food":["常山贡面","常山胡柚","球川豆腐"]},
    {"name":"开化县","att":["根宫佛国","钱江源","花牵谷","古田山国家级自然保护区"],"food":["开化气糕","青蛳","苏庄炊粉"]}
  ]},
  {"id":"zhoushan","name":"舟山市","adcode":330900,"desc":"千岛之城，中国最大的群岛地级市。海天佛国普陀山，东海渔场的鲜美之地。","attractions":["普陀山","朱家尖","东极岛","嵊泗列岛"],"food":["海鲜","带鱼","大黄鱼","螺类","海鲜面"],"districts":[
    {"name":"定海区","att":["定海古城","鸦片战争遗址公园","舟山名人馆","马岙博物馆"],"food":["定海小吃","海鲜面","金塘李子"]},
    {"name":"普陀区","att":["普陀山","朱家尖","南沙沙滩","大青山","印象普陀"],"food":["普陀素斋","海鲜大餐","佛手螺"]},
    {"name":"岱山县","att":["双合石壁","鹿栏晴沙","东沙古镇","中国台风博物馆"],"food":["岱山海鲜","蓬莱仙芝茶","虾饺"]},
    {"name":"嵊泗县","att":["嵊泗列岛","大悲山","基湖沙滩","东海渔村田岙","枸杞岛"],"food":["嵊泗贻贝","鲜活海鲜","带鱼"]}
  ]},
  {"id":"taizhou","name":"台州市","adcode":331000,"desc":"山海水城，和合圣地。天台山佛宗道源，神仙居人间仙境，海鲜美食的天堂。","attractions":["天台山","神仙居","临海古城","大陈岛","括苍山"],"food":["食饼筒","仙居杨梅","三门青蟹","黄岩蜜橘"],"districts":[
    {"name":"椒江区","att":["大陈岛","葭沚老街","一江山岛战役纪念地","海洋世界"],"food":["食饼筒","姜汤面","泡虾"]},
    {"name":"黄岩区","att":["黄岩大瀑布","柔川景区","九峰山","黄岩博物馆"],"food":["黄岩蜜橘","黄岩糟羹","麦虾"]},
    {"name":"路桥区","att":["路桥老街","飞龙湖","桐屿枇杷园","中国日用品商城"],"food":["路桥食饼筒","新桥枇杷"]},
    {"name":"临海市","att":["临海古城墙","紫阳古街","桃渚古城","括苍山","龙兴寺"],"food":["麦虾","蛋清羊尾","海苔饼"]},
    {"name":"温岭市","att":["长屿硐天","石塘镇","千年曙光园","方山","洞下沙滩"],"food":["温岭嵌糕","石塘海鲜","泡饼"]},
    {"name":"玉环市","att":["大鹿岛","漩门湾湿地","鸡山岛","玉环漩门湾国家湿地"],"food":["玉环文旦","鱼皮馄饨","番薯粉圆"]},
    {"name":"天台县","att":["天台山","国清寺","石梁飞瀑","华顶国家森林公园","济公故居"],"food":["天台饺饼筒","糊拉汰","饺菜"]},
    {"name":"仙居县","att":["神仙居","公盂景区","景星岩","高迁古民居","淡竹休闲谷"],"food":["仙居杨梅","仙居八大碗","三黄鸡"]},
    {"name":"三门县","att":["蛇蟠岛","三门核电站","湫水大峡谷","潘家小镇"],"food":["三门青蟹","三门对虾","三门甜瓜"]}
  ]},
  {"id":"lishui","name":"丽水市","adcode":331100,"desc":"浙江绿谷，中国生态第一市。九山半水半分田，摄影之乡、养生福地。","attractions":["缙云仙都","云和梯田","南尖岩","古堰画乡","百山祖"],"food":["缙云烧饼","龙泉青瓷宴","庆元香菇","遂昌黄粿"],"districts":[
    {"name":"莲都区","att":["古堰画乡","东西岩","处州府城墙","丽水南明湖"],"food":["缙云烧饼","山粉饺","处州白莲"]},
    {"name":"龙泉市","att":["龙泉山","披云山","龙泉青瓷博物馆","大窑龙泉窑遗址"],"food":["龙泉香菇","安仁粽","查田馄饨"]},
    {"name":"青田县","att":["石门洞","千峡湖","青田石雕博物馆","侨乡进口商品城"],"food":["青田田鱼","山粉饺","青田糖糕"]},
    {"name":"缙云县","att":["缙云仙都","鼎湖峰","朱潭山","小赤壁","岩下石头村"],"food":["缙云烧饼","缙云土爽面","米仁糕"]},
    {"name":"遂昌县","att":["南尖岩","金矿国家矿山公园","神龙谷","千佛山"],"food":["遂昌黄粿","遂昌长粽","高坪萝卜"]},
    {"name":"松阳县","att":["杨家堂村","松阳老街","箬寮原始林","双童山"],"food":["松阳煨盐鸡","松阳薄饼","仙草豆腐"]},
    {"name":"云和县","att":["云和梯田","云和湖","木制玩具城","坑根石寨"],"food":["云和油筒饼","山哈大席","豆腐娘"]},
    {"name":"庆元县","att":["百山祖","月山村","兰溪桥","中国香菇博物馆"],"food":["庆元香菇","灰树花","庆元甜桔柚"]},
    {"name":"景宁畲族自治县","att":["中国畲族博物馆","大均畲乡古镇","望东垟高山湿地","炉西峡"],"food":["景宁豆腐娘","畲乡粽","英川粉皮"]}
  ]}
]

# ── 5. Read template and inject data ──
print("\nGenerating HTML...")

template_path = os.path.join(os.path.dirname(__file__), "travel-map-template.html")
with open(template_path, "r", encoding="utf-8") as f:
    template = f.read()

province_json = json.dumps(province_geo, ensure_ascii=False, separators=(',', ':'))
city_geos_json = json.dumps(city_geos, ensure_ascii=False, separators=(',', ':'))
travel_json = json.dumps(travel_data, ensure_ascii=False, separators=(',', ':'))

html = template
html = html.replace("__PROVINCE_GEO__", province_json)
html = html.replace("__CITY_GEOS__", city_geos_json)
html = html.replace("__TRAVEL_DATA__", travel_json)

# ── 6. Pre-compile JSX with Babel to eliminate runtime compilation ──
print("Pre-compiling JSX with Babel...")
import re, subprocess, tempfile

# Extract JSX source from <script type="text/babel" ...>...</script>
match = re.search(
    r'<script\s+type="text/babel"[^>]*>(.*?)</script>',
    html, re.DOTALL
)
if match:
    jsx_src = match.group(1)
    # Write JSX to temp file, compile with Babel
    jsx_file = os.path.join(os.path.dirname(__file__), ".jsx_tmp.jsx")
    with open(jsx_file, "w", encoding="utf-8") as f:
        f.write(jsx_src)
    try:
        result = subprocess.run(
            ["npx", "--yes", "babel", jsx_file],
            capture_output=True, text=True, timeout=30,
            cwd=os.path.dirname(__file__)
        )
        if result.returncode == 0:
            compiled_js = result.stdout
            # Replace: remove babel standalone script, replace text/babel block with compiled JS
            html = re.sub(
                r'<script\s+src="[^"]*babel[^"]*"[^>]*></script>\s*',
                '', html
            )
            html = html.replace(
                match.group(0),
                f'<script>\n{compiled_js}\n</script>'
            )
            print("  -> JSX compiled successfully")
        else:
            print(f"  -> Babel compilation failed: {result.stderr[:200]}")
            print("  -> Falling back to runtime Babel")
    except Exception as e:
        print(f"  -> Babel not available: {e}")
        print("  -> Falling back to runtime Babel")
    finally:
        if os.path.exists(jsx_file):
            os.remove(jsx_file)
else:
    print("  -> No JSX block found, skipping compilation")

# ── 7. Write output ──
out_path = os.path.join(os.path.dirname(__file__), "travel-map.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = os.path.getsize(out_path) / 1024
print(f"\nGenerated {out_path} ({size_kb:.0f} KB)")
