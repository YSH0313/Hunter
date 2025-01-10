from dataclasses import dataclass, field
from typing import Optional, Callable, Dict


@dataclass
class Requests:
    url: str
    method: str = 'GET'
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict] = None
    data: Optional[Dict] = None
    json_params: Optional[Dict] = None
    cookies: Optional[Dict[str, str]] = None
    timeout: int = 30
    callback: Optional[Callable] = None
    meta: Dict = field(default_factory=dict)
    proxy: Optional[str] = None
    level: int = 0
    verify_ssl: Optional[bool] = None
    allow_redirects: bool = True
    is_file: bool = False
    retry_count: int = 0
    is_change: bool = False
    is_encode: Optional[bool] = None
    ignore_ip: bool = False
    is_httpx: bool = False
    is_TLS: bool = False
    is_websource: bool = False
    page_click: Optional[str] = None
    before_do: Optional[str] = None
    input_box: Optional[str] = None
    input_text: Optional[str] = None
    input_click: Optional[str] = None
    dont_filter: bool = False
    encoding: Optional[str] = None

    def __post_init__(self):
        # 可以在这里做一些后续的初始化工作
        if not self.verify_ssl and 'https' in self.url:
            self.verify_ssl = False
        if self.is_file and self.timeout == 30:
            self.timeout = 120


@dataclass
class FormRequests:
    url: str
    method: str = 'POST'
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict] = None
    data: Optional[Dict] = None
    json_params: Optional[Dict] = None
    cookies: Optional[Dict] = None
    timeout: int = 30
    callback: Optional[Callable] = None
    proxy: Optional[str] = None
    level: int = 0
    verify_ssl: Optional[bool] = None
    allow_redirects: bool = True
    is_file: bool = False
    is_httpx: bool = False
    is_TLS: bool = False
    retry_count: int = 0
    is_change: bool = False
    is_encode: Optional[bool] = None
    ignore_ip: bool = False
    dont_filter: bool = False
    encoding: Optional[str] = None
    meta: Dict = field(default_factory=dict)  # Use default_factory to ensure a new dictionary

    def __post_init__(self):
        # Adjust timeout based on certain conditions
        if self.is_file and self.timeout == 30:
            self.timeout = 120

        # Set default value for verify_ssl if it's not provided and the URL is HTTPS
        if 'https' in self.url and self.verify_ssl is None:
            self.verify_ssl = False


@dataclass
class PatchRequests:
    url: str
    method: str = 'PATCH'
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict] = None
    data: Optional[Dict] = None
    json_params: Optional[Dict] = None
    cookies: Optional[Dict] = None
    timeout: int = 30
    callback: Optional[Callable] = None
    proxy: Optional[str] = None
    level: int = 0
    verify_ssl: Optional[bool] = None
    allow_redirects: bool = True
    is_file: bool = False
    retry_count: int = 0
    is_change: bool = False
    is_encode: Optional[bool] = None
    ignore_ip: bool = False
    is_https: bool = False
    is_TLS: bool = False
    dont_filter: bool = False
    encoding: Optional[str] = None
    meta: Dict = field(default_factory=dict)  # Use default_factory to ensure a new dictionary

    def __post_init__(self):
        # Adjust timeout based on certain conditions
        if self.is_file and self.timeout == 30:
            self.timeout = 120

        # Set default value for verify_ssl if it's not provided and the URL is HTTPS
        if 'https' in self.url and self.verify_ssl is None:
            self.verify_ssl = False


@dataclass
class Response:
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    content_type: Optional[str] = None
    data: Optional[dict] = None
    cookies: Optional[Dict] = None
    text: Optional[str] = None
    content: Optional[bytes] = None
    status_code: Optional[int] = None
    xpath: Optional[str] = None
    request_info: Optional[dict] = None
    proxy: Optional[str] = None
    level: int = 0
    retry_count: int = 0
    log_info: Dict = field(default_factory=dict)
    meta: Dict = field(default_factory=dict)

    def __post_init__(self):
        # You can add additional logic here if necessary, like initializing cookies or other fields
        if not self.log_info:
            self.log_info = {}  # Ensure log_info is always a dictionary if not provided
        if not self.meta:
            self.meta = {}  # Ensure meta is always a dictionary if not provided
