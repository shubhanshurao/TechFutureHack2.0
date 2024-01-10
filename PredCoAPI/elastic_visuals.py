XYcharts = ["area", "line", "bar_stacked"]

def xyChart(param, chart_type):
    obj = {
            "attributes": {
                "title": "",
                "description": "",
                "visualizationType": "lnsXY",
                "type": "lens",
                "references": [
                    {
                        "type": "index-pattern",
                        "id": param.Device.Data_view_id,
                        "name": "indexpattern-datasource-layer-6b9f7c50-2f98-423c-8ee5-29485e1c81a9"
                    }
                ],
                "state": {
                    "visualization": {
                        "title": "Empty XY chart",
                        "legend": {
                            "isVisible": True,
                            "position": "right"
                        },
                        "valueLabels": "hide",
                        "preferredSeriesType": chart_type,
                        "layers": [
                            {
                                "layerId": "6b9f7c50-2f98-423c-8ee5-29485e1c81a9",
                                "accessors": [
                                    "22fa3745-0439-490d-b5d8-e288c76d5ccc"
                                ],
                                "position": "top",
                                "seriesType": chart_type,
                                "showGridlines": False,
                                "layerType": "data",
                                "xAccessor": "d541b80b-ecac-4adc-a203-463cbfeb137b"
                            }
                        ]
                    },
                    "query": {
                        "query": "",
                        "language": "kuery"
                    },
                    "filters": [],
                    "datasourceStates": {
                        "formBased": {
                            "layers": {
                                "6b9f7c50-2f98-423c-8ee5-29485e1c81a9": {
                                    "columns": {
                                        "22fa3745-0439-490d-b5d8-e288c76d5ccc": {
                                            "label": f"Median of {param.Name}",
                                            "dataType": "number",
                                            "operationType": "median",
                                            "sourceField": f"data.{param.Doc_field}",
                                            "isBucketed": False,
                                            "scale": "ratio",
                                            "params": {
                                                "emptyAsNull": True
                                            }
                                        },
                                        "d541b80b-ecac-4adc-a203-463cbfeb137b": {
                                            "label": "@timestamp",
                                            "dataType": "date",
                                            "operationType": "date_histogram",
                                            "sourceField": "@timestamp",
                                            "isBucketed": True,
                                            "scale": "interval",
                                            "params": {
                                                "interval": "auto",
                                                "includeEmptyRows": True,
                                                "dropPartials": False
                                            }
                                        }
                                    },
                                    "columnOrder": [
                                        "d541b80b-ecac-4adc-a203-463cbfeb137b",
                                        "22fa3745-0439-490d-b5d8-e288c76d5ccc"
                                    ],
                                    "sampling": 1,
                                    "incompleteColumns": {}
                                }
                            }
                        },
                        "textBased": {
                            "layers": {}
                        }
                    },
                    "internalReferences": [],
                    "adHocDataViews": {}
                }
            },
            "enhancements": {}
        }
    return obj
        

def pieChart(param):
    obj = {
            "attributes": {
                "title": "",
                "description": "",
                "visualizationType": "lnsPie",
                "type": "lens",
                "references": [
                    {
                        "type": "index-pattern",
                        "id": param.Device.Data_view_id,
                        "name": "indexpattern-datasource-layer-cb8e6311-3eb7-40f4-84c5-1515f95ea359"
                    }
                ],
                "state": {
                    "visualization": {
                        "shape": "pie",
                        "layers": [
                            {
                                "layerId": "cb8e6311-3eb7-40f4-84c5-1515f95ea359",
                                "primaryGroups": [
                                    "715c7466-8817-4d6d-b65e-bc17c9204326"
                                ],
                                "metrics": [
                                    "ead37273-22d0-4935-ac98-96fdac4c786b"
                                ],
                                "numberDisplay": "percent",
                                "categoryDisplay": "default",
                                "legendDisplay": "default",
                                "nestedLegend": False,
                                "layerType": "data"
                            }
                        ]
                    },
                    "query": {
                        "query": "",
                        "language": "kuery"
                    },
                    "filters": [],
                    "datasourceStates": {
                        "formBased": {
                            "layers": {
                                "cb8e6311-3eb7-40f4-84c5-1515f95ea359": {
                                    "columns": {
                                        "715c7466-8817-4d6d-b65e-bc17c9204326": {
                                            "label": "@timestamp",
                                            "dataType": "date",
                                            "operationType": "date_histogram",
                                            "sourceField": "@timestamp",
                                            "isBucketed": True,
                                            "scale": "interval",
                                            "params": {
                                                "interval": "auto",
                                                "includeEmptyRows": True,
                                                "dropPartials": False
                                            }
                                        },
                                        "ead37273-22d0-4935-ac98-96fdac4c786b": {
                                            "label": f"Median of {param.Name}",
                                            "dataType": "number",
                                            "operationType": "median",
                                            "sourceField": f"data.{param.Doc_field}",
                                            "isBucketed": False,
                                            "scale": "ratio",
                                            "params": {
                                                "emptyAsNull": True
                                            }
                                        }
                                    },
                                    "columnOrder": [
                                        "715c7466-8817-4d6d-b65e-bc17c9204326",
                                        "ead37273-22d0-4935-ac98-96fdac4c786b"
                                    ],
                                    "sampling": 1,
                                    "incompleteColumns": {}
                                }
                            }
                        },
                        "textBased": {
                            "layers": {}
                        }
                    },
                    "internalReferences": [],
                    "adHocDataViews": {}
                }
            },
            "enhancements": {}
        }
    return obj


def legacyMetricChart(param):
    obj = {
            "attributes": {
                "title": "",
                "description": "",
                "visualizationType": "lnsLegacyMetric",
                "type": "lens",
                "references": [
                    {
                        "type": "index-pattern",
                        "id": param.Device.Data_view_id,
                        "name": "indexpattern-datasource-layer-ead3adcd-4a3e-4294-a4de-bcf366effa49"
                    },
                    {
                        "type": "index-pattern",
                        "name": "268b03ba-f00a-43b8-95b2-e6c0e231a2b9",
                        "id": param.Device.Data_view_id
                    }
                ],
                "state": {
                    "visualization": {
                        "layerId": "ead3adcd-4a3e-4294-a4de-bcf366effa49",
                        "accessor": "844ae530-8e65-4a64-b2a3-20d40360af1c",
                        "layerType": "data",
                        "size": "xl",
                        "textAlign": "center",
                        "titlePosition": "bottom"
                    },
                    "query": {
                        "query": "",
                        "language": "kuery"
                    },
                    "filters": [
                        {
                            "meta": {
                                "index": "268b03ba-f00a-43b8-95b2-e6c0e231a2b9",
                                "alias": f"data.{param.Doc_field}: *",
                                "type": "custom",
                                "key": "query",
                                "value": {
                                    "bool": {
                                        "must": [],
                                        "filter": [
                                            {
                                                "bool": {
                                                    "should": [
                                                        {
                                                            "exists": {
                                                                "field": f"data.{param.Doc_field}"
                                                            }
                                                        }
                                                    ],
                                                    "minimum_should_match": 1
                                                }
                                            }
                                        ],
                                        "should": [],
                                        "must_not": []
                                    }
                                },
                                "disabled": False,
                                "negate": False
                            },
                            "query": {
                                "bool": {
                                    "must": [],
                                    "filter": [
                                        {
                                            "bool": {
                                                "should": [
                                                    {
                                                        "exists": {
                                                            "field": f"data.{param.Doc_field}"
                                                        }
                                                    }
                                                ],
                                                "minimum_should_match": 1
                                            }
                                        }
                                    ],
                                    "should": [],
                                    "must_not": []
                                }
                            },
                            "$state": {
                                "store": "appState"
                            }
                        }
                    ],
                    "datasourceStates": {
                        "formBased": {
                            "layers": {
                                "ead3adcd-4a3e-4294-a4de-bcf366effa49": {
                                    "columns": {
                                        "844ae530-8e65-4a64-b2a3-20d40360af1c": {
                                            "label": f"Last value of {param.Name}",
                                            "dataType": "number",
                                            "operationType": "last_value",
                                            "isBucketed": False,
                                            "scale": "ratio",
                                            "sourceField": f"data.{param.Doc_field}",
                                            "filter": {
                                                "query": f"data.{param.Doc_field}: *",
                                                "language": "kuery"
                                            },
                                            "params": {
                                                "sortField": "@timestamp"
                                            }
                                        }
                                    },
                                    "columnOrder": [
                                        "844ae530-8e65-4a64-b2a3-20d40360af1c"
                                    ],
                                    "sampling": 1,
                                    "incompleteColumns": {}
                                }
                            }
                        },
                        "textBased": {
                            "layers": {}
                        }
                    },
                    "internalReferences": [],
                    "adHocDataViews": {}
                }
            },
            "enhancements": {}
        }
    return obj