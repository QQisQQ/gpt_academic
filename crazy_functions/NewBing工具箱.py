from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive

@CatchException
def NewBing工具箱(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，用于灵活调整复杂功能的各种参数
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append(("这是什么功能？", "[Local Message] 使得New Bing禁止联网并且仅纠错随后的段落"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
    advanced_arg = plugin_kwargs.get("advanced_arg", "correct")

    if advanced_arg == "correct":
        i_say = r"Can you help me ensure that the grammar and the spelling is correct? " +\
                r"Do not try to polish the text, if no mistake is found, tell me that this paragraph is good." +\
                r"If you find grammar or spelling mistakes, please list mistakes you find in a two-column markdown table, " +\
                r"put the original text the first column, " +\
                r"put the corrected text in the second column and highlight the key words you fixed.""\n" +\
                r"Example:""\n" +\
                r"Paragraph: How is you? Do you knows what is it?""\n" +\
                r"| Original sentence | Corrected sentence |""\n" +\
                r"| :--- | :--- |""\n" +\
                r"| How **is** you? | How **are** you? |""\n" +\
                r"| Do you **knows** what **is** **it**? | Do you **know** what **it** **is** ? |""\n" +\
                r"The following paragraphs are taken from an academic paper. " +\
                r"You need to report all grammar and spelling mistakes following the example above and without searching the internet.""\n\n" +\
                "\"" + txt + "\"" 
    else:
        i_say = r"The following paragraphs are taken from an academic paper. Polish the writing to meet the academic style, " +\
                r"improve the spelling, grammar, clarity, concision and overall readability. When necessary, rewrite the whole sentence. Ensure without searching the internet. " +\
                r"Furthermore, list all modification and explain the reasons to do so in markdown table." + "\n\n" +\
                "\"" + txt + "\""

    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=i_say, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt=""
    )
    chatbot[-1] = (i_say, gpt_say)
    history.append(i_say);history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新