import React, { useState, useEffect, useRef } from 'react';
import { Layout, Button, Card, Spin, message, Divider, Typography, Tag, Upload, Modal, List, Popconfirm, Space, Collapse, Table } from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined, CheckCircleOutlined, CheckSquareOutlined, ClearOutlined, LeftOutlined, RightOutlined, EyeOutlined, HistoryOutlined } from '@ant-design/icons';
import axios from 'axios';
import './App.css';

const { Header, Content, Sider } = Layout;
const { Title, Text } = Typography;

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [jdFiles, setJdFiles] = useState([]);
  const [resumeFiles, setResumeFiles] = useState([]);
  const [selectedJd, setSelectedJd] = useState(null);
  const [selectedResumes, setSelectedResumes] = useState([]);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingFile, setEditingFile] = useState(null);
  const [newFileName, setNewFileName] = useState('');
  const [logs, setLogs] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const logPanelRef = useRef(null);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const [isLogPanelCollapsed, setIsLogPanelCollapsed] = useState(false);
  const [previewModalVisible, setPreviewModalVisible] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const [previewContent, setPreviewContent] = useState('');
  const [previewLoading, setPreviewLoading] = useState(false);
  const [historyResults, setHistoryResults] = useState([]);
  const [historyModalVisible, setHistoryModalVisible] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);

  useEffect(() => {
    fetchFiles();
    connectWebSocket();
    fetchHistoryResults();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const fetchFiles = async () => {
    try {
      const response = await axios.get('http://localhost:8000/list-files');
      setJdFiles(response.data.jd_files);
      setResumeFiles(response.data.resume_files);
    } catch (error) {
      message.error('Failed to load files from assets');
      console.error('Error fetching files:', error);
    }
  };

  const handleFileUpload = async (file, type) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      await axios.post(`http://localhost:8000/upload-${type}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      message.success('File uploaded successfully');
      fetchFiles();
    } catch (error) {
      message.error('Failed to upload file');
    }
    return false;
  };

  const handleDelete = async (filename, type) => {
    try {
      await axios.delete(`http://localhost:8000/delete-file/${type}/${filename}`);
      message.success('File deleted successfully');
      fetchFiles();
      if (type === 'jd' && selectedJd === filename) {
        setSelectedJd(null);
      } else if (type === 'resume') {
        setSelectedResumes(prev => prev.filter(name => name !== filename));
      }
    } catch (error) {
      message.error('Failed to delete file');
    }
  };

  const handleRename = async (oldName, type) => {
    try {
      await axios.put(`http://localhost:8000/rename-file/${type}/${oldName}`, {
        new_name: newFileName
      });
      message.success('File renamed successfully');
      fetchFiles();
      setEditModalVisible(false);
      setEditingFile(null);
      setNewFileName('');
    } catch (error) {
      message.error('Failed to rename file');
    }
  };

  const handleScreening = async () => {
    if (!selectedJd || selectedResumes.length === 0) {
      message.error('Please select both job description and at least one resume');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/screen-from-assets', {
        jd_filename: selectedJd,
        resume_filenames: selectedResumes
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      setResults(response.data);
      message.success('Screening completed successfully');
    } catch (error) {
      console.error('Error during screening:', error);
      message.error(error.message || 'Error during screening process');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAllResumes = () => {
    if (selectedResumes.length === resumeFiles.length) {
      setSelectedResumes([]);
    } else {
      setSelectedResumes([...resumeFiles]);
    }
  };

  const handleScroll = (e) => {
    const element = e.target;
    const isScrolledNearBottom = element.scrollHeight - element.scrollTop - element.clientHeight < 50;
    setShouldAutoScroll(isScrolledNearBottom);
  };

  useEffect(() => {
    if (shouldAutoScroll && logPanelRef.current) {
      logPanelRef.current.scrollTop = logPanelRef.current.scrollHeight;
    }
  }, [logs, shouldAutoScroll]);

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket Connected');
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      const logEntry = JSON.parse(event.data);
      setLogs(prev => [...prev, {
        ...logEntry,
        timestamp: new Date().toISOString()
      }]);
    };

    ws.onclose = () => {
      console.log('WebSocket Disconnected');
      setWsConnected(false);
      // Try to reconnect after 5 seconds
      setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const handlePreview = async (file, type) => {
    setPreviewFile(file);
    setPreviewModalVisible(true);
    setPreviewLoading(true);

    try {
      const response = await axios.get(`http://localhost:8000/api/preview-file/${type}/${file}`);
      if (response.status !== 200) throw new Error('Failed to load file preview');
      setPreviewContent(response.data);
    } catch (error) {
      message.error('Failed to load file preview');
      console.error('Preview error:', error);
    } finally {
      setPreviewLoading(false);
    }
  };

  const renderLogPanel = () => (
    <div className={`log-panel ${isLogPanelCollapsed ? 'collapsed' : ''}`}>
      <div 
        className="log-panel-toggle"
        onClick={() => setIsLogPanelCollapsed(!isLogPanelCollapsed)}
      >
        {isLogPanelCollapsed ? <LeftOutlined /> : <RightOutlined />}
      </div>
      <div className="log-panel-header">
        <span className="log-panel-title">Processing Logs</span>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <Button
            type="text"
            size="small"
            onClick={() => setShouldAutoScroll(!shouldAutoScroll)}
            style={{ color: shouldAutoScroll ? '#52c41a' : undefined }}
          >
            Auto-scroll
          </Button>
          <Button
            type="text"
            icon={<ClearOutlined />}
            onClick={clearLogs}
            className="clear-logs-button"
          >
            Clear
          </Button>
        </div>
      </div>
      <div 
        className="log-panel-content" 
        ref={logPanelRef}
        onScroll={handleScroll}
      >
        {logs.map((log, index) => (
          <div key={index} className={`log-entry ${log.level}`}>
            <span className="log-entry-time">{new Date(log.timestamp).toLocaleTimeString()}</span>
            {log.message}
          </div>
        ))}
      </div>
    </div>
  );

  const renderFileList = (files, type) => (
    <div className="file-list-container">
      <List
        className={`${type}-list`}
        itemLayout="horizontal"
        dataSource={files}
        renderItem={(file, index) => {
          const isSelected = type === 'jd' 
            ? selectedJd === file
            : selectedResumes.includes(file);

          return (
            <List.Item
              className={`file-list-item ${isSelected ? 'selected-file' : ''}`}
              onClick={() => {
                if (type === 'jd') {
                  setSelectedJd(selectedJd === file ? null : file);
                } else {
                  setSelectedResumes(prev => 
                    prev.includes(file) ? 
                    prev.filter(name => name !== file) : 
                    [...prev, file]
                  );
                }
              }}
            >
              <div className="file-item-content">
                <div className="file-name">
                  <span className="file-index">{String(index + 1).padStart(2, '0')}</span>
                  <span className="file-name-text">{file}</span>
                  <div className="file-actions">
                    <Button
                      type="text"
                      icon={<EyeOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePreview(file, type);
                      }}
                    />
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingFile({ name: file, type });
                        setNewFileName(file);
                        setEditModalVisible(true);
                      }}
                    />
                    <Button
                      type="text"
                      icon={<DeleteOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(file, type);
                      }}
                    />
                  </div>
                </div>
              </div>
            </List.Item>
          );
        }}
      />
    </div>
  );

  const renderResults = () => {
    if (!results || !results.candidates) return null;

    return (
      <div className="results-container">
        <List
          className="candidates-list"
          dataSource={results.candidates}
          renderItem={(candidate, index) => (
            <List.Item>
              <Card className="candidate-card">
                <div className="score-section">
                  <Typography.Title level={4} style={{ margin: 0 }}>
                    {candidate.file_name}
                  </Typography.Title>
                  <Space>
                    <Tag color="blue">总分: {(candidate.evaluation.overall_score * 100).toFixed(1)}%</Tag>
                    <Tag color={candidate.evaluation.overall_score >= 0.7 ? 'green' : 'orange'}>
                      {candidate.evaluation.recommendation}
                    </Tag>
                  </Space>
                </div>

                <Divider>技能列表</Divider>
                <div className="skills-section">
                  {(candidate.candidate_info.skills || []).map((skill, i) => (
                    <Tag key={i} color="blue">{skill}</Tag>
                  ))}
                </div>

                <Divider>教育经历</Divider>
                {(candidate.candidate_info.education || []).map((edu, i) => (
                  <div key={i} className="education-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <Text strong>{edu.degree}</Text>
                      {edu.is_qs_top20 && (
                        <Tag color="magenta">QS Top 20</Tag>
                      )}
                      {edu.is_985 && !edu.is_qs_top20 && (
                        <Tag color="purple">985高校</Tag>
                      )}
                      {edu.is_211 && !edu.is_985 && !edu.is_qs_top20 && (
                        <Tag color="gold">211高校</Tag>
                      )}
                    </div>
                    <Text>{edu.institution} ({edu.year})</Text>
                    {edu.major && <Text type="secondary"> - {edu.major}</Text>}
                  </div>
                ))}

                <Divider>工作经历</Divider>
                {(candidate.candidate_info.experience || []).map((exp, i) => (
                  <div key={i} className="experience-item">
                    <Text strong>{exp.title} at {exp.company}</Text>
                    <Text type="secondary"> ({exp.duration})</Text>
                    <ul>
                      {(exp.responsibilities || []).map((resp, j) => (
                        <li key={j}>{resp}</li>
                      ))}
                    </ul>
                  </div>
                ))}

                <Collapse 
                  ghost 
                  style={{ marginTop: '16px' }}
                  items={[
                    {
                      key: '1',
                      label: <Typography.Title level={5} style={{ margin: 0 }}>详细分析</Typography.Title>,
                      children: (
                        <div className="analysis-section">
                          <div className="analysis-item">
                            <Typography.Title level={5} style={{ marginBottom: '4px' }}>技能匹配</Typography.Title>
                            <Typography.Paragraph style={{ marginBottom: '8px' }}>
                              {candidate.evaluation.analysis.skills_analysis}
                            </Typography.Paragraph>
                            <Tag color="blue">匹配度: {(candidate.evaluation.scores.skills_match * 100).toFixed(1)}%</Tag>
                          </div>

                          <div className="analysis-item">
                            <Typography.Title level={5} style={{ marginBottom: '4px' }}>经验匹配</Typography.Title>
                            <Typography.Paragraph style={{ marginBottom: '8px' }}>
                              {candidate.evaluation.analysis.experience_analysis}
                            </Typography.Paragraph>
                            <Tag color="blue">匹配度: {(candidate.evaluation.scores.experience_match * 100).toFixed(1)}%</Tag>
                          </div>

                          <div className="analysis-item">
                            <Typography.Title level={5} style={{ marginBottom: '4px' }}>教育背景</Typography.Title>
                            <Typography.Paragraph style={{ marginBottom: '8px' }}>
                              {candidate.evaluation.analysis.education_analysis}
                            </Typography.Paragraph>
                            <Tag color="blue">匹配度: {(candidate.evaluation.scores.education_match * 100).toFixed(1)}%</Tag>
                          </div>

                          <div className="analysis-item">
                            <Typography.Title level={5} style={{ marginBottom: '4px' }}>整体评估</Typography.Title>
                            <Typography.Paragraph style={{ marginBottom: '8px' }}>
                              {candidate.evaluation.analysis.overall_analysis}
                            </Typography.Paragraph>
                          </div>
                        </div>
                      )
                    }
                  ]}
                />
              </Card>
            </List.Item>
          )}
        />
      </div>
    );
  };

  const fetchHistoryResults = async () => {
    try {
      const response = await axios.get('http://localhost:8000/list-results');
      setHistoryResults(response.data.results);
    } catch (error) {
      message.error('获取历史记录失败');
    }
  };

  const loadHistoryResult = async (filename) => {
    try {
      const response = await axios.get(`http://localhost:8000/get-result/${filename}`);
      setResults(response.data.result);
      setHistoryModalVisible(false);
      message.success('已加载历史结果');
    } catch (error) {
      message.error('加载历史结果失败');
    }
  };

  const HistoryModal = () => {
    const columns = [
      {
        title: '筛选时间',
        dataIndex: 'timestamp',
        key: 'timestamp',
        render: (text) => new Date(text).toLocaleString(),
        sorter: (a, b) => new Date(b.timestamp) - new Date(a.timestamp),
      },
      {
        title: 'JD文件',
        dataIndex: 'jd_file',
        key: 'jd_file',
      },
      {
        title: '操作',
        key: 'action',
        render: (_, record) => (
          <Button type="link" onClick={() => loadHistoryResult(record.filename)}>
            加载结果
          </Button>
        ),
      },
    ];

    return (
      <Modal
        title="历史筛选结果"
        open={historyModalVisible}
        onCancel={() => setHistoryModalVisible(false)}
        footer={null}
        width={800}
      >
        <Table
          dataSource={historyResults}
          columns={columns}
          rowKey="filename"
          pagination={{ pageSize: 10 }}
        />
      </Modal>
    );
  };

  return (
    <Layout className="app-layout">
      <Header className="header">
        <Title level={2} style={{ color: 'white', margin: 0 }}>
          Resume Screen VE
        </Title>
      </Header>
      <Layout className="main-layout">
        <Sider width={360} className="file-management-sider" style={{ position: 'sticky', top: 0, height: '100vh', overflowY: 'auto' }}>
          <Card 
            title="Resumes" 
            extra={
              <div className="resume-header-actions">
                <Button
                  type="text"
                  icon={<CheckSquareOutlined 
                    style={{ color: selectedResumes.length === resumeFiles.length ? '#52c41a' : undefined }} 
                  />}
                  onClick={handleSelectAllResumes}
                />
                <Upload 
                  accept=".pdf,.docx"
                  beforeUpload={file => handleFileUpload(file, 'resume')}
                  showUploadList={false}
                >
                  <Button type="text" icon={<PlusOutlined />} />
                </Upload>
              </div>
            }
            style={{ height: '100%' }}
          >
            {renderFileList(resumeFiles, 'resume')}
          </Card>
        </Sider>
        <Layout>
          <Sider width={288} className="file-management-sider reduced-margin" style={{ position: 'sticky', top: 0, height: '100vh', overflowY: 'auto' }}>
            <div className="jd-section" style={{ height: '100%' }}>
              <Card 
                title="Job Descriptions" 
                extra={
                  <Space>
                    <Upload 
                      accept=".pdf,.docx"
                      beforeUpload={file => handleFileUpload(file, 'jd')}
                      showUploadList={false}
                    >
                      <Button type="text" icon={<PlusOutlined />} />
                    </Upload>
                    <Button 
                      icon={<HistoryOutlined />} 
                      onClick={() => setHistoryModalVisible(true)}
                      title="查看历史结果"
                    />
                  </Space>
                }
                style={{ height: 'calc(100% - 60px)' }}
              >
                {renderFileList(jdFiles, 'jd')}
              </Card>
              <Button 
                type="primary" 
                size="large"
                onClick={handleScreening}
                loading={loading}
                disabled={!selectedJd || selectedResumes.length === 0}
                className="screen-button"
                style={{ 
                  marginTop: '16px',
                  width: '100%',
                  marginLeft: '0',
                  marginRight: '0'
                }}
              >
                Start Screening
              </Button>
            </div>
          </Sider>
          <Content className={`content ${!isLogPanelCollapsed ? 'with-log' : ''}`} style={{ overflowY: 'auto', height: '100vh' }}>
            {loading ? (
              <div className="loading-container">
                <Spin size="large" />
                <Text>Processing resumes...</Text>
              </div>
            ) : renderResults()}
          </Content>
          {renderLogPanel()}
        </Layout>
        <HistoryModal />
      </Layout>

      <Modal
        title="Rename File"
        open={editModalVisible}
        onOk={() => handleRename(editingFile?.name, editingFile?.type)}
        onCancel={() => {
          setEditModalVisible(false);
          setEditingFile(null);
          setNewFileName('');
        }}
      >
        <input
          value={newFileName}
          onChange={e => setNewFileName(e.target.value)}
          style={{ width: '100%', padding: '8px' }}
        />
      </Modal>

      <Modal
        title={previewFile}
        open={previewModalVisible}
        onCancel={() => setPreviewModalVisible(false)}
        width={800}
        footer={null}
      >
        {previewLoading ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <Spin />
          </div>
        ) : (
          <pre style={{ 
            maxHeight: '60vh', 
            overflow: 'auto', 
            padding: '16px',
            backgroundColor: '#f5f5f5',
            borderRadius: '4px'
          }}>
            {previewContent}
          </pre>
        )}
      </Modal>
    </Layout>
  );
}

export default App; 