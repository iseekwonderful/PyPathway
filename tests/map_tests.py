from pypathway import *
from echarts import *
import random


class MappingAPITest:
    # this class test all the imagable situation while using mapping API
    @staticmethod
    def test_value_change(target="KEGG"):
        vc_default = ValueChanged({
            NP.BG_COLOR: rgb(255, 0, 0),
            NP.OPACITY: 1,
            NP.SCALE: 1,
            NP.COLOR: rgb(255, 255, 255)
        })
        vc_mouse_over = ValueChanged({
            NP.BG_COLOR: rgb(0, 255, 0),
            NP.SCALE: 1.5
        })
        vc_left = VC({
            NP.BG_COLOR: rgb(0, 0, 255),
            NP.SCALE: 1.2,
            NP.OPACITY: 0,
            NP.COLOR: "red"
        })
        vc_right = VC({
            NP.BG_COLOR: rgb(0, 0, 0),
            NP.SCALE: 2,
            NP.COLOR: "white"
        })
        vo = VisualizationOption(default=[vc_default], over=[vc_mouse_over],
                                 click=[vc_left])
        return MappingAPITest.draw_test_vo_in(vo, target)

    @staticmethod
    def draw_test_vo_in(vo, target, query_id=False):
        if target not in ["KEGG", "WP", "Reactome"]:
            target = "KEGG"
        if target == "KEGG":
            # res = PublicDatabase.search_kegg("b cell")
            res = PublicDatabase.search_kegg("jak")
            path = res[0].load()
            ids = [x.id for x in path.genes]
        elif target == "WP":
            res = PublicDatabase.search_wp("jak")
            path = res[2].load()
            # for x in path.flatten():
            #     if x.props.get("GraphId") == "c501b":
            #         print(x.summary())
            ids = [x.props.get("GraphId") for x in path.nodes]
            # ids = [x.props.get("GraphId") for x in path.flatten() if x.props.get("GraphId") is not None]
            print(ids)
        else:
            res = PublicDatabase.search_reactome("jak")  #, proxies=proxy)
            path = res[1].load(1.3)
            ids = [x.id for x in path.nodes if x.type == "macromolecule" or x.type == "macromolecule multimer"]
        if query_id:
            return ids, path
        else:
            path.integrate(ids, [vo for _ in range(len(ids))])
            return path.draw()

    @staticmethod
    def test_hyper_link(target="KEGG"):
        hp = HyperLink(name="Google", url="http://www.google.com")
        hp_left = HyperLink(name="github", url="http://www.github.com")
        vo = VisualizationOption(default=[], over=[hp], click=[hp_left])
        return MappingAPITest.draw_test_vo_in(vo, target)

    @staticmethod
    def test_popup_windows(target="KEGG"):
        # containg 1 tab
        vc_default = ValueChanged({
            NP.BG_COLOR: rgb(255, 0, 0),
            NP.OPACITY: 1,
            NP.SCALE: 1,
            NP.COLOR: rgb(255, 255, 255)
        })
        pp_over = PopUp([ImageTab(name="Google",
                                 image_path="https://www.google.com/logos/doodles/2016/434th-anniversary-of-the-introduction-of-the-gregorian-calendar-5700260446863360-hp.jpg")])
        it = ImageTab(name="Image",
                                 image_path="https://www.google.com/logos/doodles/2016/434th-anniversary-of-the-introduction-of-the-gregorian-calendar-5700260446863360-hp.jpg")
        tt = TableTab(name="Table", table=[["date", "data"], ["1", "0.23"], ["2", "2.23"]])
        txt = TextTab("Text", text="Hello World, my friend")
        chart = Echart("percentage")
        chart.use(Pie("%", data=[random.randint(10, 30), random.randint(10, 30)]))
        ct = ChartTab("Pie-Chart", chart.json)
        pp_left = PopUp([it, tt, ct, txt])
        vo = VisualizationOption(over=[pp_over], click=[pp_left])
        return MappingAPITest.draw_test_vo_in(vo, target)

    @staticmethod
    def test_connection(target="KEGG"):
        ids, path = MappingAPITest.draw_test_vo_in(None, target, True)
        vos = []
        for x in ids:
            vos.append(VisualizationOption(over=[
                Connection([Edge(x, width=3, line_style="dashed",
                                 line_color="#ff8800",
                                 target_style=ValueChanged({
                                            NP.BG_COLOR: rgb(123, 254, 0),
                                            NP.OPACITY: 1,
                                            NP.SCALE: 1.5,
                                            NP.COLOR: rgb(255, 255, 255)
                                        })
                                 ) for x in random.sample(ids, 5)])
            ]))
        path.integrate(ids, vos)
        return path.draw()


