from abc import ABC
from . import utils
from . import node


class Connection(ABC):
    """Abstract class for all connections

    Attributes
    ----------
    id : str
        Connection ID

    contents : ContentsType
        Contents moving through the node

    source : Node
        Starting point of the connection

    sink : Node
        Endpoint of the connection

    tags : dict of Tag
        Data tags associated with this connection

    bidirectional : bool
        whether flow can go from sink to source. False by default
    """

    id: str = NotImplemented
    contents: utils.ContentsType = NotImplemented
    source: node.Node = NotImplemented
    sink: node.Node = NotImplemented
    tags: dict = NotImplemented
    bidirectional: bool = False

    def __repr__(self):
        return (
            f"<wwtp_configuration.connection.Connection id:{self.id} "
            f"contents:{self.contents} source:{self.source.id} sink:{self.sink.id} "
            f"tags:{self.tags} bidirectional:{self.bidirectional}>\n"
        )

    def set_flow_rate(self, min, max, avg):
        """Set the minimum, maximum, and average flow rate through the connection

        Parameters
        ----------
        min : int
            Minimum flow rate through the connection

        max : int
            Maximum flow rate through the connection

        avg : int
            Average flow rate through the connection
        """
        # TODO: attach units to flow rate
        self.flow_rate = (min, max, avg)

    def set_pressure(self, min, max, avg):
        """Set the minimum, maximum, and average pressure inside the connection

        Parameters
        ----------
        min : int
            Minimum pressure inside the connection

        max : int
            Maximum pressure inside the connection

        avg : int
            Average pressure inside the connection
        """
        # TODO: attach units to flow rate
        self.pressure = (min, max, avg)

    def add_tag(self, tag):
        """Adds a tag to the node

        Parameters
        ----------
        tag : Tag
            Tag object to add to the node
        """
        self.tags[tag.id] = tag

    def remove_tag(self, tag_name):
        """Removes a tag from the node

        Parameters
        ----------
        tag_name : str
            name of tag to remove
        """
        del self.tags[tag_name]


class Pipe(Connection):
    """
    Parameters
    ---------
    id : str
        Pipe ID

    contents : ContentsType
        Contents moving through the connection

    source : Node
        Starting point of the connection

    sink : Node
        Endpoint of the connection

    min_flow : int
        Minimum flow rate through the pipe

    max_flow : int
        Maximum flow rate through the pipe

    avg_flow : int
        Average flow rate through the pipe

    diameter : int
        Pipe diameter in meters

    friction_coeff : int
        Friction coefficient for the pipe

    min_pres : int
        Minimum pressure inside the pipe

    max_pres : int
        Maximum pressure inside the pipe

    avg_pres : int
        Average pressure inside the pipe

    tags : dict of Tag
        Data tags associated with this pump

    bidirectional : bool
        whether flow can go from sink to source. False by default

    Attributes
    ----------
    id : str
        Pipe ID

    contents : ContentsType
        Contents moving through the connection.

    source : Node
        Starting point of the connection

    sink : Node
        Endpoint of the connection

    flow_rate : tuple
        Minimum, maximum, and average flow rate through the pipe

    diameter : int
        Pipe diameter in meters

    friction_coeff : int
        Friction coefficient for the pipe

    pressure : tuple
        Minimum, maximum, and average pressure in the pipe

    tags : dict of Tag
        Data tags associated with this pipe

    bidirectional : bool
        whether flow can go from sink to source. False by default
    """

    def __init__(
        self,
        id,
        contents,
        source,
        sink,
        min_flow,
        max_flow,
        avg_flow,
        diameter=None,
        friction=None,
        min_pres=None,
        max_pres=None,
        avg_pres=None,
        tags={},
        bidirectional=False,
    ):
        self.id = id
        self.contents = contents
        self.source = source
        self.sink = sink
        self.diameter = diameter
        self.friction_coeff = friction
        self.set_pressure(min_pres, max_pres, avg_pres)
        self.set_flow_rate(min_flow, max_flow, avg_flow)
        self.tags = tags
        self.bidirectional = bidirectional

    def __repr__(self):
        return (
            f"<wwtp_configuration.connection.Pipe id:{self.id} "
            f"contents:{self.contents} source:{self.source.id} sink:{self.sink.id} "
            f"flow_rate:{self.flow_rate} pressure:{self.pressure} "
            f"diameter:{self.diameter} friction_coeff:{self.friction_coeff} "
            f"tags:{self.tags} bidirectional:{self.bidirectional}>\n"
        )

    def __eq__(self, other):
        if not isinstance(other, Pipe):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.id == other.id
            and self.contents == other.contents
            and self.source == other.source
            and self.sink == other.sink
            and self.diameter == other.diameter
            and self.friction_coeff == other.friction_coeff
            and self.pressure == other.pressure
            and self.flow_rate == other.flow_rate
            and self.tags == other.tags
            and self.bidirectional == other.bidirectional
        )


class Pump(Connection):
    """
    Parameters
    ----------
    id : str
        Pump ID

    input_contents : ContentsType
        Contents entering the pump.

    output_contents : ContentsType
        Contents leaving the pump.

    elevation : int
        Elevation of the pump in meters above sea level

    horsepower : int
        Horsepower of a single pump

    num_units : int
        Number of pumps running in parallel

    min_flow : int
        Minimum flow rate supplied by the pump

    max_flow : int
        Maximum flow rate supplied by the pump

    avg_flow : int
        Average flow rate supplied by the pump

    pump_type : PumpType
        Type of pump (either VFD or constant)

    tags : dict of Tag
        Data tags associated with this pump

    bidirectional : bool
        whether flow can go from sink to source. False by default

    Attributes
    ----------
    id : str
        Pump ID

    input_contents : ContentsType
        Contents entering the pump.

    output_contents : ContentsType
        Contents leaving the pump.

    elevation : int
        Elevation of the pump in meters above sea level

    horsepower : int
        Horsepower of a single pump

    num_units : int
        Number of pumps running in parallel

    flow_rate : tuple
        Tuple of minimum, maximum, and average pump flow rate

    tags : dict of Tag
        Data tags associated with this pump

    bidirectional : bool
        whether flow can go from sink to source. False by default

    energy_efficiency : function
        Function which takes in the current flow rate and returns the energy
        required to pump at that rate
    """

    def __init__(
        self,
        id,
        contents,
        source,
        sink,
        min_flow,
        max_flow,
        avg_flow,
        elevation,
        horsepower,
        num_units,
        pump_type=utils.PumpType.Constant,
        tags={},
        bidirectional=False,
    ):
        self.id = id
        self.contents = contents
        self.source = source
        self.sink = sink
        self.elevation = elevation
        self.pump_type = pump_type
        self.horsepower = horsepower
        self.num_units = num_units
        self.tags = tags
        self.set_flow_rate(min_flow, max_flow, avg_flow)
        self.set_energy_efficiency(None)
        self.bidirectional = bidirectional

    def __repr__(self):
        return (
            f"<wwtp_configuration.connection.Pump id:{self.id} "
            f"contents:{self.contents} source:{self.source.id} sink:{self.sink.id} "
            f"flow_rate:{self.flow_rate} elevation:{self.elevation} "
            f"horsepower:{self.horsepower} num_units:{self.num_units} "
            f"tags:{self.tags} bidirectional:{self.bidirectional}>\n"
        )

    def __eq__(self, other):
        # don't attempt to compare against unrelated types
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.id == other.id
            and self.contents == other.contents
            and self.source == other.source
            and self.sink == other.sink
            and self.elevation == other.elevation
            and self.pump_type == other.pump_type
            and self.horsepower == other.horsepower
            and self.num_units == other.num_units
            and self.tags == other.tags
            and self.flow_rate == other.flow_rate
            and self.energy_efficiency == other.energy_efficiency
            and self.bidirectional == other.bidirectional
        )

    def set_pump_type(self, pump_type):
        """Set the pump curve to the given function

        Parameters
        ----------
        pump_type : PumpType
        """
        # TODO: check that pump_type is a valid enum
        self.pump_type = pump_type

    def set_energy_efficiency(self, pump_curve):
        """Set the pump curve to the given function

        Parameters
        ----------
        pump_curve : function
            function which takes in the current flow rate and returns the energy
            required to pump at that rate
        """
        # TODO: type check that pump_curve is a function
        self.energy_efficiency = pump_curve


class Wire(Connection):
    """
    Parameters
    ---------
    id : str
        Pipe ID

    source : Node
        Starting point of the connection

    sink : Node
        Endpoint of the connection

    tags : dict of Tag
        Data tags associated with this pump

    bidirectional
        whether electricity can flow from sink to source. False by default

    Attributes
    ----------
    id : str
        Pipe ID

    contents : ContentsType
        Contents moving through the connection.

    source : Node
        Starting point of the connection

    sink : Node
        Endpoint of the connection

    tags : dict of Tag
        Data tags associated with this pipe

    bidirectional
        whether electricity can flow from sink to source. False by default
    """

    def __init__(self, id, source, sink, tags={}, bidirectional=False):
        self.id = id
        self.source = source
        self.sink = sink
        self.tags = tags
        self.bidirectional = bidirectional
        self.contents = utils.ContentsType.Electricity

    def __repr__(self):
        return (
            f"<wwtp_configuration.connection.Wire id:{self.id} "
            f"contents:{self.contents} source:{self.source.id} sink:{self.sink.id} "
            f"tags:{self.tags} bidirectional:{self.bidirectional}>\n"
        )

    def __eq__(self, other):
        if not isinstance(other, Pipe):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.id == other.id
            and self.contents == other.contents
            and self.source == other.source
            and self.sink == other.sink
            and self.tags == other.tags
            and self.bidirectional == other.bidirectional
        )
