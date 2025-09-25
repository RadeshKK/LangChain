from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda,RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


def response_by_model(api_key,text):

    model=ChatGoogleGenerativeAI(model="gemini-1.5-pro",temperature=0.6,api_key=api_key)

    # ----------------------------------------------------------------------------------------------------------------------------------------

    first_prompt = ChatPromptTemplate.from_messages(messages=[
    ("system", "You are a content generator AI model who produces positive content only.Content is restricted to have exactly 150 words only."),
    ("human", "Generate a good quality content on the given topic: {topic}. Ensure it is easy to understand.")])


    # ---------------------------------------------------------------------------------------------------------------------------------------
    # fb work here
    def fb_content(content):
        """This function is used to prompt according to the facebook post."""
        
        fb_prompt=ChatPromptTemplate.from_messages([
            ("system","You create engaging, high-quality Facebook posts with a friendly, conversational tone. Use emojis, hashtags, and call-to-actions for maximum engagement. Keep content concise, visually appealing, and optimized for social sharing while maintaining a positive style. Content is restricted to have exactly 150 words only.Do not generate link."),
            ("human","Generate given content according to facebook post: {content}. Keep your content short, fun, and interactive! Add emojis, use trending hashtags, and always include a strong call-to-action.")
        ])
        
        return fb_prompt.format_prompt(content=content)



    fb_chain=(
        RunnableLambda(lambda x:fb_content(x)) | model | StrOutputParser()
    )



    # ----------------------------------------------------------------------------------------------------------------------------------------
    #linkedin work here


    def linkedin_content(content):
        """This is used for linkedin prompting"""
        
        linkedin_prompt = ChatPromptTemplate.from_messages([
                ("system", "You create professional, engaging, and high-quality LinkedIn posts. Your content should be insightful, value-driven, and formatted to encourage networking and professional discussions. Use a formal yet approachable tone, incorporate relevant hashtags, and include a clear call-to-action for engagement. Keep posts structured, informative, and optimized for LinkedIn's audience.Content is restricted to have exactly 150 words only.Do not generate link."),
                ("human", "Generate the given content as a LinkedIn post: {content}. Make it professional, insightful, and engaging. Use industry-relevant hashtags, maintain clarity, and encourage meaningful interactions.")])
        
        return linkedin_prompt.format_prompt(content=content)


    linkedin_chain=(
        RunnableLambda(lambda x:linkedin_content(x)) | model | StrOutputParser()
    )

    # ------------------------------------------------------------------------------------------------------------------------------------------

    def showing_both_content(content1,content2):
        """Combining the content of the both to display"""
        return {"fb_tips":content1,"linkedin_tips":content2}

    # -----------------------------------------------------------------------------------------------------------------------------------------#
    # """ Using Chains to connect each components easily"""
    chain= (
        first_prompt|
        model|
        StrOutputParser()|
        RunnableParallel(branches={"facebook": fb_chain, "linkedin": linkedin_chain})|
        RunnableLambda(lambda x: showing_both_content(x["branches"]["facebook"], x["branches"]["linkedin"]))
    )

    response=chain.invoke({"topic":text})

    return response

