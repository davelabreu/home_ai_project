import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useConfig } from '../hooks/useConfig'; // Corrected import path

interface Message {
  text: string;
  sender: 'user' | 'ollama';
}

const ChatCard: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { monitor_target_host_set, monitorTargetHost, monitorTargetPort, loading: configLoading, error: configError } = useConfig();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const newUserMessage: Message = { text: inputMessage, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setInputMessage('');
    setIsSending(true);

    try {
      // Determine the API URL based on whether a remote host is configured
      const targetHost = monitorTargetHost || 'localhost';
      // If monitoring a remote host, use its configured port. Otherwise, assume local Flask app is on 5000.
      const targetPort = monitor_target_host_set && monitorTargetPort ? monitorTargetPort : '5000';
      const chatApiUrl = `http://${targetHost}:${targetPort}/api/chat`;

      const response = await fetch(chatApiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: inputMessage }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const ollamaResponse: Message = { text: data.response || data.error || 'Error: No response from Ollama', sender: 'ollama' };
      setMessages((prevMessages) => [...prevMessages, ollamaResponse]);
    } catch (error: any) {
      const errorMessage: Message = { text: `Error: ${error.message}`, sender: 'ollama' };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  // Chat is disabled if config is still loading or if there's a config error for the remote host.
  // It is NOT disabled if monitorTargetHost is null (i.e., when on the Jetson's local dashboard).
  const isChatDisabled = configLoading || (monitor_target_host_set && configError !== null);

  return (
    <Card className="col-span-1 md:col-span-2 lg:col-span-1 h-[500px] flex flex-col">
      <CardHeader>
        <CardTitle>Chat with Jetson AI (Ollama)</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col space-y-4 overflow-hidden">
        <div className="flex-1 overflow-y-auto pr-4 -mr-4"> {/* Custom scrollbar handling */}
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex mb-2 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] p-2 rounded-lg ${
                  msg.sender === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        {configError && !monitor_target_host_set && ( // Display error if config fails and it's not remote monitoring
          <p className="text-center text-red-500 mt-2">
            Error loading chat configuration: {configError}
          </p>
        )}
        {(configLoading || (!monitor_target_host_set && configError)) && (
             <p className="text-center text-muted-foreground mt-2">
                {configLoading ? "Loading chat configuration..." : "Chat unavailable due to configuration error."}
             </p>
        )}
        <div className="flex mt-auto space-x-2 p-2 border-t dark:border-gray-700">
          <Input
            type="text"
            placeholder="Type your message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !isSending && !isChatDisabled) {
                handleSendMessage();
              }
            }}
            disabled={isSending || isChatDisabled}
            className="flex-1"
          />
          <Button onClick={handleSendMessage} disabled={isSending || isChatDisabled}>
            {isSending ? 'Sending...' : 'Send'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ChatCard;
