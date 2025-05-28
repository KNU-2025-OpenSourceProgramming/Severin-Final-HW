const { useState, useEffect, useRef } = React; // 引入 React 钩子 (Hooks)

const App = () => {
    // `cameraMode` 状态：'environment' (后置摄像头) 或 'user' (前置摄像头)
    const [cameraMode, setCameraMode] = useState('environment');
    // `detections` 状态：存储检测到的对象列表
    const [detections, setDetections] = useState([]);
    // `isProcessing` 状态：表示是否正在处理图像
    const [isProcessing, setIsProcessing] = useState(false);
    // `errorMessage` 状态：存储错误信息
    const [errorMessage, setErrorMessage] = useState('');

    // `useRef` 用于直接访问 DOM 元素，例如 <video> 和 <canvas>
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const streamRef = useRef(null); // 存储媒体流对象
    const timerRef = useRef(null);   // 存储 setInterval 的 ID

    // `useEffect` 钩子用于在组件加载和 `cameraMode` 变化时启动/停止摄像头
    useEffect(() => {
        startCamera(); // 启动摄像头
        // 返回一个清理函数，在组件卸载或 `cameraMode` 变化前执行
        return () => {
            stopCamera(); // 停止摄像头
            if (timerRef.current) {
                clearInterval(timerRef.current); // 清除定时器
            }
        };
    }, [cameraMode]); // 依赖数组，当 `cameraMode` 变化时重新运行此 effect

    // 启动摄像头功能
    const startCamera = async () => {
        try {
            if (streamRef.current) {
                stopCamera(); // 如果已有流，则先停止
            }
            // 摄像头约束，设置 `facingMode` 来选择前置或后置摄像头
            const constraints = {
                video: {
                    facingMode: cameraMode
                }
            };
            // 获取用户媒体设备 (摄像头) 的视频流
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            streamRef.current = stream; // 保存流对象

            if (videoRef.current) {
                videoRef.current.srcObject = stream; // 将视频流设置到 <video> 元素
                videoRef.current.play(); // 播放视频

                // 当视频元数据加载完成后 (获取到视频的真实宽度和高度)
                videoRef.current.onloadedmetadata = () => {
                    if (canvasRef.current) {
                        // 设置 canvas 的宽度和高度与视频保持一致
                        canvasRef.current.width = videoRef.current.videoWidth;
                        canvasRef.current.height = videoRef.current.videoHeight;
                    }

                    // 周期性地执行对象检测
                    timerRef.current = setInterval(() => {
                        // 只有当前没有正在处理的请求时才进行检测
                        if (!isProcessing) {
                            detectObjects();
                        }
                    }, 100); // 每 x毫秒行一次
                };
            }
        } catch (err) {
            setErrorMessage(`카메라 접근 오류 (Camera Access Error): ${err.message}`);
            console.error('카메라 접근 오류 (Camera Access Error):', err);
        }
    };

    // 停止摄像头功能
    const stopCamera = () => {
        if (streamRef.current) {
            // 遍历所有媒体轨道（Track）并停止
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null; // 清空流对象
        }
    };

    // 切换摄像头功能 (前置 <-> 后置)
    const switchCamera = () => {
        setCameraMode(prev => prev === 'environment' ? 'user' : 'environment');
    };

    // 捕获图像，将当前视频帧绘制到 canvas 并转换为 Base64 格式的 JPEG 图像数据
    const captureImage = () => {
        if (!videoRef.current || !canvasRef.current) return null;

        const canvas = document.createElement('canvas'); // 创建一个离屏 canvas
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;

        const ctx = canvas.getContext('2d'); // 获取 2D 渲染上下文
        // 将视频当前帧绘制到 canvas 上
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

        // 将 canvas 内容转换为 Base64 编码的 JPEG 图像数据 URL
        return canvas.toDataURL('image/jpeg');
    };

    // 对象检测功能，向后端 API 发送图像数据
    const detectObjects = async () => {
        if (!videoRef.current || !canvasRef.current) return;

        try {
            setIsProcessing(true); // 设置处理状态为真
            const imageData = captureImage(); // 捕获图像数据

            if (!imageData) {
                console.error('이미지 캡처 실패 (Image Capture Failed)');
                return;
            }

            // 发送 POST 请求到 `/api/detect`
            const response = await fetch('/api/detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // 设置请求头为 JSON
                },
                body: JSON.stringify({ image: imageData }), // 将图像数据作为 JSON 发送
            });

            const result = await response.json(); // 解析 JSON 响应

            if (result.success) {
                console.log('감지 결과 (Detection Results):', result.detections);
                setDetections(result.detections);     // 更新检测结果状态
                drawDetections(result.detections);    // 在 canvas 上绘制检测框
            } else {
                console.error('객체 감지 오류 (Object Detection Error):', result.error);
                setErrorMessage(`객체 감지 오류 (Object Detection Error): ${result.error}`);
            }
        } catch (err) {
            console.error('API 요청 오류 (API Request Error):', err);
            setErrorMessage(`API 요청 오류 (API Request Error): ${err.message}`);
        } finally {
            setIsProcessing(false); // 无论成功或失败，都将处理状态设为假
        }
    };

    // 在 canvas 上绘制检测到的对象边界框和标签
    const drawDetections = (detectionResults) => {
        if (!canvasRef.current || !videoRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        // 清空 canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 计算缩放比例，以便在 canvas 上正确绘制
        const scaleX = canvas.width / videoRef.current.videoWidth;
        const scaleY = canvas.height / videoRef.current.videoHeight;

        // 遍历每个检测结果并绘制
        detectionResults.forEach(detection => {
            const [x1, y1, x2, y2] = detection.bbox; // 获取边界框坐标
            // 根据缩放比例调整坐标
            const scaledX1 = x1 * scaleX;
            const scaledY1 = y1 * scaleY;
            const scaledWidth = (x2 - x1) * scaleX;
            const scaledHeight = (y2 - y1) * scaleY;

            // 绘制边界框
            ctx.strokeStyle = '#00FF00'; // 绿色边框
            ctx.lineWidth = 2;
            ctx.strokeRect(scaledX1, scaledY1, scaledWidth, scaledHeight);

            // 绘制文本背景
            const label = `${detection.name} ${Math.round(detection.confidence * 100)}%`; // 标签 (名称 + 置信度)
            const textWidth = ctx.measureText(label).width;
            ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'; // 半透明黑色背景
            ctx.fillRect(scaledX1, scaledY1 - 20, textWidth + 10, 20);

            // 绘制文本
            ctx.fillStyle = '#FFFFFF'; // 白色文字
            ctx.font = '16px Arial';
            ctx.fillText(label, scaledX1 + 5, scaledY1 - 5);
        });
    };

    // 渲染检测到的对象列表
    const renderDetectionList = () => {
        if (detections.length === 0) {
            return <p>감지된 객체가 없습니다 (No objects detected).</p>;
        }

        // 按类别分组检测结果
        const groupedDetections = {};
        detections.forEach(detection => {
            const name = detection.name;
            if (!groupedDetections[name]) {
                groupedDetections[name] = 0;
            }
            groupedDetections[name]++;
        });

        return (
            <div>
                <h5>감지된 객체 (Detected Objects)</h5>
                {/* 渲染每个类别的计数 */}
                {Object.entries(groupedDetections).map(([name, count], index) => (
                    <div key={index} className="detection-item">
                        <span>{name}</span>
                        <span className="badge bg-primary">{count}</span>
                    </div>
                ))}
                <p className="mt-2">총 {detections.length}개 객체 감지됨 (Total {detections.length} objects detected)</p>
            </div>
        );
    };

    // 组件的渲染内容
    return (
        <div className="container">
            <h1 className="text-center mb-4">YOLOv8 객체 인식 (Object Detection)</h1>

            {/* 显示错误信息 */}
            {errorMessage && (
                <div className="alert alert-danger" role="alert">
                    {errorMessage}
                </div>
            )}

            <div className="camera-container">
                <video ref={videoRef} id="videoElement" autoPlay playsInline></video>
                <canvas ref={canvasRef} id="canvasElement"></canvas>
            </div>

            <div className="controls mt-3">
                {/* 切换摄像头按钮 */}
                <button
                    className="btn btn-primary"
                    onClick={switchCamera}
                >
                    {cameraMode === 'environment' ? '전면 카메라로 전환 (Switch to Front Camera)' : '후면 카메라로 전환 (Switch to Rear Camera)'}
                </button>

                {/* 对象检测按钮，正在处理时禁用 */}
                <button
                    className="btn btn-success"
                    onClick={detectObjects}
                    disabled={isProcessing}
                >
                    객체 감지 (Detect Objects)
                    {/* 正在处理时显示加载动画 */}
                    {isProcessing && (
                        <span className="spinner-border spinner-border-sm ms-2" role="status" aria-hidden="true"></span>
                    )}
                </button>
            </div>

            {/* 显示检测到的对象列表 */}
            <div className="detection-list mt-3">
                {renderDetectionList()}
            </div>
        </div>
    );
};

// 将 App 组件渲染到 ID 为 'app' 的 DOM 元素中
ReactDOM.render(<App />, document.getElementById('app'));
