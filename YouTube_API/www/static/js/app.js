const { useState, useEffect } = React;

function VideoDetailsModal({ video, onClose }) {
  if (!video) return null;
  
  return (
    <div className="modal fade show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{video.title}</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <div className="ratio ratio-16x9 mb-3">
              <iframe 
                src={`https://www.youtube.com/embed/${video.id}`} 
                title={video.title}
                allowFullScreen>
              </iframe>
            </div>
            <h6 className="text-muted">{video.channelTitle}</h6>
            <p className="text-muted small">发布于: {new Date(video.publishedAt).toLocaleString()}</p>
            <p>{video.description}</p>
          </div>
          <div className="modal-footer">
            <a 
              href={`https://www.youtube.com/watch?v=${video.id}`} 
              className="btn btn-danger" 
              target="_blank"
              rel="noopener noreferrer"
            >
              在 YouTube 上观看
            </a>
            <button type="button" className="btn btn-secondary" onClick={onClose}>关闭</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function VideoCard({ video, onVideoSelect }) {
  return (
    <div className="col-md-4">
      <div className="card video-card">
        <img
           src={video.thumbnailUrl}
           className="card-img-top thumbnail"
           alt={video.title}
           style={{ cursor: 'pointer' }}
           onClick={() => onVideoSelect(video)}
        />
        <div className="card-body">
          <h5 className="card-title">{video.title}</h5>
          <p className="card-text text-muted">{video.channelTitle}</p>
          <p className="card-text small">{video.description.substring(0, 100)}...</p>
          <button
            className="btn btn-primary me-2"
            onClick={() => onVideoSelect(video)}
          >
            详情
          </button>
          <a
             href={`https://www.youtube.com/watch?v=${video.id}`}
             className="btn btn-danger"
             target="_blank"
            rel="noopener noreferrer"
          >
            <i className="bi bi-play-fill"></i> 동영상 보기
          </a>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [query, setQuery] = useState('');
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState(null);

  const searchVideos = async (e) => {
    e.preventDefault(); // 阻止表单默认提交行为

    if (!query.trim()) return; // 如果查询为空，则不执行搜索

    setLoading(true);
    setError(null);

    try {
      // 注意这里的 API 请求路径是相对路径，因为ngrok会将请求转发到本地的Flask服务器
      const response = await fetch(`/api/search?query=${encodeURIComponent(query)}&max_results=12`);
      const data = await response.json();

      if (response.ok) {
        setVideos(data.videos);
      } else {
        setError(data.error || '검색 중 오류가 발생했습니다.');
        setVideos([]);
      }
    } catch (err) {
      setError('서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.');
      setVideos([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container my-5">
      <div className="row mb-4">
        <div className="col">
          <h1 className="text-center mb-4">YouTube 视频搜索</h1>

          <form onSubmit={searchVideos}>
            <div className="input-group mb-3">
              <input
                type="text"
                className="form-control"
                placeholder="输入关键词搜索视频"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button className="btn btn-primary" type="submit">
                搜索
              </button>
            </div>
          </form>

          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <div className="row">
          {videos.length > 0 ? (
            videos.map((video) => (
              <VideoCard 
                key={video.id} 
                video={video} 
                onVideoSelect={setSelectedVideo} 
              />
            ))
          ) : (
            !loading && !error && query && (
              <p className="text-center">没有找到相关视频。</p>
            )
          )}
        </div>
      )}
      
      {selectedVideo && (
        <VideoDetailsModal 
          video={selectedVideo} 
          onClose={() => setSelectedVideo(null)} 
        />
      )}
    </div>
  );
}

const rootElement = document.getElementById('root');
ReactDOM.render(<App />, rootElement);
