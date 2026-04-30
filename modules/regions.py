from dataclasses import dataclass


@dataclass
class RegionInfo:
    name: str
    code: str
    hosts: list[str]


REGIONS: list[RegionInfo] = [
    RegionInfo("Asia Pacific (Hong Kong)", "ap-east-1", ["ec2.ap-east-1.amazonaws.com", "gamelift-ping.ap-east-1.api.aws"]),
    RegionInfo("Asia Pacific (Mumbai)", "ap-south-1", ["gamelift.ap-south-1.amazonaws.com", "gamelift-ping.ap-south-1.api.aws"]),
    RegionInfo("Asia Pacific (Seoul)", "ap-northeast-2", ["gamelift.ap-northeast-2.amazonaws.com", "gamelift-ping.ap-northeast-2.api.aws"]),
    RegionInfo("Asia Pacific (Singapore)", "ap-southeast-1", ["gamelift.ap-southeast-1.amazonaws.com", "gamelift-ping.ap-southeast-1.api.aws"]),
    RegionInfo("Asia Pacific (Sydney)", "ap-southeast-2", ["gamelift.ap-southeast-2.amazonaws.com", "gamelift-ping.ap-southeast-2.api.aws"]),
    RegionInfo("Asia Pacific (Tokyo)", "ap-northeast-1", ["gamelift.ap-northeast-1.amazonaws.com", "gamelift-ping.ap-northeast-1.api.aws"]),
    RegionInfo("Canada (Central)", "ca-central-1", ["gamelift.ca-central-1.amazonaws.com", "gamelift-ping.ca-central-1.api.aws"]),
    RegionInfo("Europe (Frankfurt)", "eu-central-1", ["gamelift.eu-central-1.amazonaws.com", "gamelift-ping.eu-central-1.api.aws"]),
    RegionInfo("Europe (Ireland)", "eu-west-1", ["gamelift.eu-west-1.amazonaws.com", "gamelift-ping.eu-west-1.api.aws"]),
    RegionInfo("Europe (London)", "eu-west-2", ["gamelift.eu-west-2.amazonaws.com", "gamelift-ping.eu-west-2.api.aws"]),
    RegionInfo("South America (São Paulo)", "sa-east-1", ["gamelift.sa-east-1.amazonaws.com", "gamelift-ping.sa-east-1.api.aws"]),
    RegionInfo("US East (N. Virginia)", "us-east-1", ["gamelift.us-east-1.amazonaws.com", "gamelift-ping.us-east-1.api.aws"]),
    RegionInfo("US East (Ohio)", "us-east-2", ["gamelift.us-east-2.amazonaws.com", "gamelift-ping.us-east-2.api.aws"]),
    RegionInfo("US West (N. California)", "us-west-1", ["gamelift.us-west-1.amazonaws.com", "gamelift-ping.us-west-1.api.aws"]),
    RegionInfo("US West (Oregon)", "us-west-2", ["gamelift.us-west-2.amazonaws.com", "gamelift-ping.us-west-2.api.aws"]),
]

regions_by_code: dict[str, RegionInfo] = {r.code: r for r in REGIONS}
display_order: list[str] = [r.code for r in REGIONS]
