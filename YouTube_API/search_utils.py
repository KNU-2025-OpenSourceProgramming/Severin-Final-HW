import time
from googleapiclient.errors import HttpError

def search_with_retry(youtube_service, query, max_results, retries=3):
    """
    带重试机制的 YouTube 搜索函数
    :param youtube_service: 构建好的 youtube API 服务对象
    :param query: 搜索关键词
    :param max_results: 最大结果数
    :param retries: 最大重试次数
    :return: API 响应
    :raises: Exception 如果所有重试都失败
    """
    for attempt in range(retries):
        try:
            search_response = youtube_service.search().list(
                q=query,
                part="snippet",
                maxResults=max_results,
                type="video"
            ).execute()
            return search_response
        except HttpError as e:
            # 检查是否是可重试的错误（例如 429 Too Many Requests, 5xx 服务器错误）
            if e.resp.status in [429, 500, 502, 503, 504] and attempt < retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                print(f"API 错误 ({e.resp.status})，第 {attempt + 1} 次重试，等待 {wait_time} 秒...")
                time.sleep(wait_time)
                continue
            else:
                raise e # 非重试错误或已达到最大重试次数
        except Exception as e:
            # 处理其他通用错误
            raise e
    raise Exception("所有重试尝试均失败。") # 理论上不会执行到这里
