import streamlit as st
import boto3
from botocore.exceptions import ClientError

# Set the page title and icon
st.set_page_config(page_title="🦜🔗 Chatbot App", page_icon="🤖")

# Sidebar for model selection
model_options = {
    "Anthropic: Claude 3 Sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "Anthropic: Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Sidebar Setup (select model)

st.sidebar.title("Model Selection")
selected_model = st.sidebar.selectbox(
    "Select Model", options=list(model_options.keys()), index=0
)


# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Stream response from AWS Bedrock Converse via boto3
def generate_response(prompt):
    """Stream response from AWS Bedrock Converse and yield text chunks for st.write_stream."""
    bedrock = boto3.client('bedrock-runtime')
    # Build messages list: include past user/assistant messages and current user message
    msgs = []
    for msg in st.session_state.messages:
        msgs.append({"role": msg["role"], "content": [{"text": msg["content"]}]})
    msgs.append({"role": "user", "content": [{"text": prompt}]})
    try:
        resp = bedrock.converse_stream(
            modelId=model_options[selected_model],
            messages=msgs,
        )
        stream = resp.get('stream', [])
    except ClientError as e:
        print("Client error: %s", e)
        return iter([f"Error: {e.response['Error']['Message']}"])

    # Generator yielding text deltas
    full_resp = []
    def gen():
        for event in stream:
            if 'contentBlockDelta' in event:
                delta = event['contentBlockDelta']['delta']['text']
                full_resp.append(delta)
                yield delta
        # After stream, append full assistant message
        st.session_state.messages.append({"role": "assistant", "content": ''.join(full_resp)})
    return gen()


# Input field for user message
if prompt := st.chat_input("Enter your message here..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Stream assistant response
    response_iter = generate_response(prompt)
    with st.chat_message("assistant"):
        st.write_stream(response_iter)
